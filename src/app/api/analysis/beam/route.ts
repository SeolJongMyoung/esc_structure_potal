import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();

        // Define path to python script
        const scriptPath = path.join(process.cwd(), 'scripts', 'rc_beam_calc.py');

        // Use python or python3 depending on environment
        const runPython = (cmd: string): Promise<string> => {
            return new Promise((resolve, reject) => {
                const pythonProcess = spawn(cmd, [scriptPath]);
                let resultData = '';
                let errorData = '';

                pythonProcess.stdin.write(JSON.stringify(body));
                pythonProcess.stdin.end();

                pythonProcess.stdout.on('data', (data) => resultData += data.toString());
                pythonProcess.stderr.on('data', (data) => errorData += data.toString());

                pythonProcess.on('close', (code) => {
                    if (code !== 0) reject(errorData);
                    else resolve(resultData);
                });

                pythonProcess.on('error', (err) => reject(err.message));
            });
        };

        let output;
        try {
            output = await runPython('python');
        } catch (e) {
            // If 'python' fails, try 'python3'
            try {
                output = await runPython('python3');
            } catch (e2) {
                console.error('Python execution failed:', e, e2);
                return NextResponse.json({ error: 'Python not found or script error' }, { status: 500 });
            }
        }

        try {
            const results = JSON.parse(output);
            return NextResponse.json(results);
        } catch (e) {
            return NextResponse.json({ error: 'Invalid result format' }, { status: 500 });
        }

    } catch (error) {
        console.error('API Error:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
