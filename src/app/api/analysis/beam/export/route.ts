import { NextRequest, NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const { material, rows } = body;

        // Start Python process
        const scriptPath = path.join(process.cwd(), "scripts", "rc_beam_calc.py");
        const pythonProcess = spawn("python", [scriptPath]);

        let outputData = "";
        let errorData = "";

        // Send input to Python
        const inputStr = JSON.stringify({ mode: "export", material, rows });
        pythonProcess.stdin.write(inputStr);
        pythonProcess.stdin.end();

        return new Promise<NextResponse>((resolve) => {
            pythonProcess.stdout.on("data", (data) => {
                outputData += data.toString();
            });

            pythonProcess.stderr.on("data", (data) => {
                errorData += data.toString();
            });

            pythonProcess.on("close", (code) => {
                if (code !== 0) {
                    console.error("Python Error:", errorData);
                    return resolve(NextResponse.json({ error: "Python Execution Failed", details: errorData }, { status: 500 }));
                }

                try {
                    const result = JSON.parse(outputData);
                    if (result.success && result.file) {
                        const filePath = result.file;
                        if (fs.existsSync(filePath)) {
                            const fileBuffer = fs.readFileSync(filePath);

                            // Optional: Delete the temp file after reading if needed, 
                            // but usually it's better to let OS clean temp dir or handle manually.

                            return resolve(new NextResponse(fileBuffer, {
                                status: 200,
                                headers: {
                                    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    "Content-Disposition": `attachment; filename="RC_Beam_Report.xlsx"`,
                                },
                            }));
                        } else {
                            return resolve(NextResponse.json({ error: "File Not Found" }, { status: 500 }));
                        }
                    } else {
                        return resolve(NextResponse.json({ error: "Export Failed", details: result }, { status: 500 }));
                    }
                } catch (e) {
                    console.error("Parse Error:", e, outputData);
                    return resolve(NextResponse.json({ error: "Failed to parse result", output: outputData }, { status: 500 }));
                }
            });
        });

    } catch (error: any) {
        console.error("API Error:", error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
