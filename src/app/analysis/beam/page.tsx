"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function RCBeamAnalysisPage() {
    const [material, setMaterial] = useState({
        fck: 35,
        fy: 400,
        phi_f: 0.85,
        phi_v: 0.75
    });
    const [designStandard, setDesignStandard] = useState("강도설계법(도로교 설계기준, 2010)");
    const [isFileMenuOpen, setIsFileMenuOpen] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const router = useRouter();

    const [rows, setRows] = useState([
        {
            id: 1,
            name: "Center",
            Mu: 1000, Vu: 50, Nu: 5, Ms: 80,
            H: 800, B: 1000,
            dc1: 80, dia1: 25, num1: 8,
            dc2: 0, dia2: 0, num2: 0,
            dc3: 0, dia3: 0, num3: 0,
            crack_case: "일반환경",
            av_dia: 0, av_leg: 0, av_space: 0,
            as_req: 0, as_used: 0, as_ratio: 0, Mr: 0, Mr_rate: 0, Vn: 0, Vn_rate: 0, V_reinf: "-", fs: 0, crack_status: "-",
            is_calculating: false, is_calculated: false, selected: false
        }
    ]);

    const [selectAll, setSelectAll] = useState(false);

    const handleAddRow = () => {
        setRows(prev => [
            ...prev,
            {
                id: prev.length > 0 ? Math.max(...prev.map(r => r.id)) + 1 : 1,
                name: "",
                Mu: 0, Vu: 0, Nu: 0, Ms: 0,
                H: 0, B: 0,
                dc1: 80, dia1: 13, num1: 0,
                dc2: 0, dia2: 0, num2: 0,
                dc3: 0, dia3: 0, num3: 0,
                crack_case: "일반환경",
                av_dia: 0, av_leg: 0, av_space: 0,
                as_req: 0, as_used: 0, as_ratio: 0, Mr: 0, Mr_rate: 0, Vn: 0, Vn_rate: 0, V_reinf: "-", fs: 0, crack_status: "-",
                is_calculating: false, is_calculated: false, selected: false
            }
        ]);
    };

    const handleDeleteRow = () => {
        const remainingRows = rows.filter(row => !row.selected);
        if (remainingRows.length === 0 && rows.length > 0) {
            // Keep at least one empty row if everything is deleted
            setRows([{
                id: 1, name: "", Mu: 0, Vu: 0, Nu: 0, Ms: 0, H: 0, B: 0,
                dc1: 80, dia1: 13, num1: 0, dc2: 0, dia2: 0, num2: 0, dc3: 0, dia3: 0, num3: 0,
                crack_case: "일반환경", av_dia: 0, av_leg: 0, av_space: 0,
                as_req: 0, as_used: 0, as_ratio: 0, Mr: 0, Mr_rate: 0, Vn: 0, Vn_rate: 0, V_reinf: "-", fs: 0, crack_status: "-",
                is_calculating: false, is_calculated: false, selected: false
            }]);
        } else {
            setRows(remainingRows);
        }
        setSelectAll(false);
    };

    const handleToggleSelectAll = () => {
        const newState = !selectAll;
        setSelectAll(newState);
        setRows(prev => prev.map(row => ({ ...row, selected: newState })));
    };

    const handleToggleSelect = (index: number) => {
        const newRows = [...rows];
        newRows[index].selected = !newRows[index].selected;
        setRows(newRows);
        setSelectAll(newRows.every(row => row.selected));
    };

    const handleMaterialChange = (e: React.ChangeEvent<HTMLInputElement>, key: string) => {
        setMaterial(prev => ({ ...prev, [key]: parseFloat(e.target.value) || 0 }));
        // Reset results and calculated status for all rows when materials change
        setRows(prev => prev.map(row => ({
            ...row,
            is_calculated: false,
            as_req: 0,
            as_used: 0,
            as_ratio: 0,
            Mr: 0,
            Mr_rate: 0,
            Vn: 0,
            Vn_rate: 0,
            V_reinf: "-",
            fs: 0,
            crack_status: "-"
        })));
    };

    const handleRowChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>, index: number, key: string) => {
        let value: string | number;
        if (key === 'name' || key === 'crack_case') {
            value = e.target.value;
        } else {
            const val = e.target.value;
            // Allow typing: empty, minus sign, trailing dot, or trailing zeros after a dot
            if (val === "" || val === "-" || val.endsWith(".") || (val.includes(".") && val.endsWith("0"))) {
                value = val;
            } else {
                value = e.target.tagName === 'SELECT' ? (parseInt(val) || 0) : (parseFloat(val) || 0);
            }
        }

        setRows(prev => prev.map((row, i) => {
            if (i === index) {
                const isNameChange = key === 'name';
                return {
                    ...row,
                    [key]: value,
                    is_calculated: isNameChange ? row.is_calculated : false,
                    // Clear results if it's not a name or crack_case change? 
                    // Actually, crack_case change SHOULD reset results because it affects calculation.
                    as_req: isNameChange ? row.as_req : 0,
                    as_used: isNameChange ? row.as_used : 0,
                    as_ratio: isNameChange ? row.as_ratio : 0,
                    Mr: isNameChange ? row.Mr : 0,
                    Mr_rate: isNameChange ? (row as any).Mr_rate : 0,
                    Vn: isNameChange ? (row as any).Vn : 0,
                    Vn_rate: isNameChange ? (row as any).Vn_rate : 0,
                    V_reinf: isNameChange ? (row as any).V_reinf : "-",
                    fs: isNameChange ? row.fs : 0,
                    crack_status: isNameChange ? (row as any).crack_status : "-"
                };
            }
            return row;
        }));
    };

    const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
        e.target.select();
    };

    const handleKeyDown = (e: React.KeyboardEvent, rowIndex: number, colIndex: number) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            // Try to find the next column in the same row
            let nextInput = document.querySelector(`[data-row="${rowIndex}"][data-col="${colIndex + 1}"]`) as HTMLElement;

            if (!nextInput) {
                // If last column, move to first column of the next row
                nextInput = document.querySelector(`[data-row="${rowIndex + 1}"][data-col="0"]`) as HTMLElement;
            }

            if (nextInput) {
                nextInput.focus();
                // Auto-open select dropdown if it's a select element
                if (nextInput.tagName === 'SELECT') {
                    try { (nextInput as any).showPicker(); } catch (err) { }
                }
            }
        }
    };

    const handleSelectFocus = (e: React.FocusEvent<HTMLSelectElement>) => {
        try { (e.target as any).showPicker(); } catch (err) { }
    };

    const handleCalculate = async () => {
        // Find rows that have input (e.g., name or dimensions)
        const validRows = rows.filter(r => r.H > 0 && r.B > 0);
        if (validRows.length === 0) return;

        setRows(prev => prev.map(row => (row.H > 0 && row.B > 0 ? { ...row, is_calculating: true } : row)));

        try {
            const response = await fetch('/api/analysis/beam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ design_standard: designStandard, material, rows: validRows })
            });

            if (response.ok) {
                const results = await response.json();

                // Update Material phi values from the first valid result if available
                if (results.length > 0 && !results[0].error) {
                    setMaterial(prev => ({
                        ...prev,
                        phi_f: results[0].phi_f,
                        phi_v: results[0].phi_v
                    }));
                }

                // Map results back to rows
                setRows(prev => {
                    let resultIdx = 0;
                    return prev.map(row => {
                        if (row.H > 0 && row.B > 0) {
                            const res = results[resultIdx++];
                            if (res && !res.error) {
                                return {
                                    ...row,
                                    as_req: res.as_req,
                                    as_used: res.as_used,
                                    as_ratio: res.as_ratio,
                                    Mr: res.Mr,
                                    Mr_rate: res.Mr_rate,
                                    Vn: res.Vn,
                                    Vn_rate: res.Vn_rate,
                                    V_reinf: res.V_reinf,
                                    fs: res.fs,
                                    crack_status: res.crack_status,
                                    is_calculated: true,
                                    is_calculating: false
                                };
                            }
                        }
                        return { ...row, is_calculating: false };
                    });
                });
            } else {
                setRows(prev => prev.map(row => ({ ...row, is_calculating: false })));
                alert("Calculation failed. Please check your inputs.");
            }
        } catch (error) {
            console.error("Calculation Error:", error);
            setRows(prev => prev.map(row => ({ ...row, is_calculating: false })));
            alert("An error occurred during calculation.");
        }
    };

    const handleExport = async () => {
        console.log("=== handleExport START ===");
        const selectedRows = rows.filter(row => row.selected);
        console.log("Selected rows count:", selectedRows.length);

        if (selectedRows.length === 0) {
            console.log("No rows selected, showing alert");
            window.alert("엑셀로 내보낼 행을 먼저 선택해주세요.");
            return;
        }

        // Check if all selected rows have calculation results
        const rowsMissingResults = selectedRows.filter(row => !row.is_calculated);
        console.log("Rows missing results:", rowsMissingResults.length);

        if (rowsMissingResults.length > 0) {
            console.log("Some rows missing calculation, showing alert");
            window.alert("단면검토를 수행한 후 출력하세요");
            return;
        }

        console.log("All validations passed, starting export fetch...");

        try {
            const response = await fetch("/api/analysis/beam/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ design_standard: designStandard, material, rows: selectedRows })
            });

            console.log("Fetch response status:", response.status);
            console.log("Fetch response ok:", response.ok);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Export API error:", errorText);
                throw new Error("Export failed: " + errorText);
            }

            const blob = await response.blob();
            console.log("Blob size:", blob.size);
            console.log("Blob type:", blob.type);

            if (blob.size === 0) {
                console.error("Received empty blob!");
                window.alert("파일이 비어있습니다. 서버 오류를 확인해주세요.");
                return;
            }

            const fileName = `RC_Beam_Report_${new Date().getTime()}.xlsx`;

            // Method 1: Try navigator.msSaveBlob for Edge/IE
            if ((navigator as any).msSaveBlob) {
                console.log("Using msSaveBlob method");
                (navigator as any).msSaveBlob(blob, fileName);
                console.log("=== handleExport END (msSaveBlob) ===");
                return;
            }

            // Method 2: Create a proper File object and use it
            const file = new File([blob], fileName, {
                type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            });
            const url = URL.createObjectURL(file);
            console.log("File URL created:", url);

            // Create link and trigger download
            const link = document.createElement("a");
            link.href = url;
            link.download = fileName;
            link.style.visibility = "hidden";
            link.style.position = "absolute";
            link.style.left = "-9999px";
            document.body.appendChild(link);

            console.log("Clicking download link...");
            link.click();

            // Cleanup after delay
            window.setTimeout(() => {
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                console.log("Cleanup completed");
            }, 2000);

            console.log("=== handleExport END (success) ===");
            window.alert("다운로드가 시작되었습니다. 다운로드 폴더를 확인하세요.");

        } catch (error) {
            console.error("=== handleExport ERROR ===", error);
            window.alert("엑셀 내보내기 중 오류가 발생했습니다: " + (error as Error).message);
        }
    };




    const [isReportModalOpen, setIsReportModalOpen] = useState(false);
    const [reportData, setReportData] = useState<any>(null);
    const [activeReportTab, setActiveReportTab] = useState("total");
    const [viewingRowName, setViewingRowName] = useState("");

    const handleView = async () => {
        const selectedRows = rows.filter(row => row.selected);
        if (selectedRows.length === 0) {
            alert("조회할 행을 먼저 선택해주세요.");
            return;
        }
        if (selectedRows.length > 1) {
            alert("계산과정은 한 번에 한 행만 조회할 수 있습니다.");
            return;
        }
        if (!selectedRows[0].is_calculated) {
            alert("단면검토를 수행한 후 조회하세요.");
            return;
        }

        const targetRow = selectedRows[0];
        setViewingRowName(targetRow.name || `Row ${targetRow.id}`);

        try {
            const response = await fetch('/api/analysis/beam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mode: 'report',
                    design_standard: designStandard,
                    material,
                    rows: [targetRow]
                })
            });

            if (response.ok) {
                const data = await response.json();
                setReportData(data);
                setIsReportModalOpen(true);
                setActiveReportTab("total");
            } else {
                alert("Report generation failed.");
            }
        } catch (error) {
            console.error("View Error:", error);
            alert("An error occurred while fetching the report.");
        }
    };

    const copyToClipboard = () => {
        if (!reportData) return;
        const textToCopy = reportData[activeReportTab];
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert("클립보드에 복사되었습니다.");
        });
    };

    const saveToTextFile = () => {
        if (!reportData) return;
        const textToSave = reportData[activeReportTab];
        const blob = new Blob([textToSave], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `Calculation_Report_${viewingRowName}_${activeReportTab}.txt`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const isAnyRowSelected = rows.some(row => row.selected);
    const isCalculating = rows.some(row => row.is_calculating);

    const toolbarButtons = [
        { label: isCalculating ? "Calculating..." : "Calc", icon: "📊", onClick: handleCalculate, disabled: isCalculating },
        { label: "Export", icon: "📄", onClick: handleExport, disabled: isCalculating },
        { label: "View", icon: "👁️", onClick: handleView, disabled: isCalculating }
    ];

    const handleNew = () => {
        if (confirm("새 프로젝트를 시작하시겠습니까? 현재 입력된 데이터는 저장되지 않을 수 있습니다.")) {
            setRows([{
                id: 1, name: "Center", Mu: 1000, Vu: 50, Nu: 5, Ms: 80, H: 800, B: 1000,
                dc1: 80, dia1: 25, num1: 8, dc2: 0, dia2: 0, num2: 0, dc3: 0, dia3: 0, num3: 0,
                crack_case: "일반환경", av_dia: 0, av_leg: 0, av_space: 0,
                as_req: 0, as_used: 0, as_ratio: 0, Mr: 0, Mr_rate: 0, Vn: 0, Vn_rate: 0, V_reinf: "-", fs: 0, crack_status: "-",
                is_calculating: false, is_calculated: false, selected: false
            }]);
            setMaterial({ fck: 35, fy: 400, phi_f: 0.85, phi_v: 0.75 });
            setIsFileMenuOpen(false);
        }
    };

    const handleSave = () => {
        const data = { designStandard, material, rows };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `Project_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        setIsFileMenuOpen(false);
    };

    const handleOpen = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target?.result as string);
                if (data.designStandard) setDesignStandard(data.designStandard);
                if (data.material) setMaterial(data.material);
                if (data.rows) setRows(data.rows);
                setIsFileMenuOpen(false);
            } catch (err) {
                alert("파일을 불러오는 중 오류가 발생했습니다.");
            }
        };
        reader.readAsText(file);
    };

    const handleExit = () => {
        if (confirm("종료하시겠습니까?")) {
            router.push('/dashboard');
        }
    };

    return (
        <main style={{ minHeight: '100vh', backgroundColor: '#f0f0f0', color: '#333', display: 'flex', flexDirection: 'column' }}>
            {/* Hidden File Input */}
            <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".json"
                onChange={handleFileChange}
            />

            {/* Top Menu Bar */}
            <div style={{ backgroundColor: '#fff', borderBottom: '1px solid #ccc', padding: '2px 10px', display: 'flex', gap: '20px', fontSize: '12px' }}>
                <span onClick={() => setIsFileMenuOpen(true)} style={{ cursor: 'pointer', padding: '2px 5px', fontWeight: 'bold' }}>파일</span>
                {["Calc", "View", "도움말"].map(item => (
                    <span key={item} style={{ cursor: 'pointer', padding: '2px 5px' }}>{item}</span>
                ))}
            </div>

            {/* File Menu Overlay */}
            {isFileMenuOpen && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                    backgroundColor: 'rgba(0,0,0,0.4)', zIndex: 2000, display: 'flex'
                }}>
                    <div style={{
                        width: '300px', backgroundColor: '#3b82f6', color: '#fff',
                        display: 'flex', flexDirection: 'column', height: '100%',
                        boxShadow: '4px 0 10px rgba(0,0,0,0.1)'
                    }}>
                        {/* File Menu Header */}
                        <div style={{ display: 'flex', alignItems: 'center', padding: '10px 20px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                            <button onClick={() => setIsFileMenuOpen(false)} style={{ background: 'none', border: 'none', color: '#fff', fontSize: '24px', cursor: 'pointer', marginRight: '15px' }}>←</button>
                            <span style={{ fontSize: '18px', fontWeight: 'bold' }}>File</span>
                            <div style={{ marginLeft: 'auto', backgroundColor: '#fff', color: '#3b82f6', padding: '4px 12px', fontSize: '12px', borderRadius: '4px' }}>Home</div>
                        </div>

                        {/* File Menu Items */}
                        <div style={{ flex: 1, padding: '20px 0' }}>
                            <div onClick={handleNew} style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
                                <span style={{ fontSize: '15px' }}>New</span>
                            </div>
                            <div onClick={handleOpen} style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                                <span style={{ fontSize: '15px' }}>Open</span>
                            </div>
                            <div onClick={handleSave} style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                                <span style={{ fontSize: '15px' }}>Save</span>
                            </div>
                            <div onClick={handleSave} style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline><path d="M12 18l3-3m0 0l-3-3m3 3H9"></path></svg>
                                <span style={{ fontSize: '15px' }}>Save as</span>
                            </div>

                            <div style={{ height: '1px', backgroundColor: 'rgba(255,255,255,0.1)', margin: '15px 0' }}></div>

                            <div style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px', opacity: 0.7 }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
                                <span style={{ fontSize: '15px' }}>Import</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px', opacity: 0.7 }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
                                <span style={{ fontSize: '15px' }}>Export</span>
                            </div>

                            <div style={{ height: '1px', backgroundColor: 'rgba(255,255,255,0.1)', margin: '15px 0' }}></div>

                            <div onClick={handleExit} style={{ display: 'flex', alignItems: 'center', padding: '12px 30px', cursor: 'pointer', gap: '15px' }}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                                <span style={{ fontSize: '15px' }}>Exit</span>
                            </div>
                        </div>

                        {/* File Menu Footer */}
                        <div style={{ padding: '20px', fontSize: '11px', opacity: 0.5 }}>
                            CivilPortal v0.1.0
                        </div>
                    </div>
                    <div onClick={() => setIsFileMenuOpen(false)} style={{ flex: 1, cursor: 'pointer' }}></div>
                </div>
            )}

            {/* Toolbar */}
            <div style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #ccc', padding: '5px 10px', display: 'flex', gap: '10px' }}>
                {toolbarButtons.map(btn => (
                    <button
                        key={btn.label}
                        onClick={btn.disabled ? undefined : btn.onClick}
                        disabled={btn.disabled}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px',
                            padding: '4px 12px',
                            backgroundColor: btn.disabled ? '#f0f0f0' : '#fff',
                            border: '1px solid #ccc',
                            borderRadius: '4px',
                            fontSize: '13px',
                            cursor: btn.disabled ? 'not-allowed' : 'pointer',
                            boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                            color: btn.disabled ? '#999' : '#333',
                            opacity: btn.disabled ? 0.7 : 1
                        }}
                    >
                        <span>{btn.icon}</span>
                        <span>{btn.label}</span>
                    </button>
                ))}
            </div>

            {/* Tabs Area */}
            <div style={{ padding: '10px 10px 0', display: 'flex', gap: '2px' }}>
                <div style={{ padding: '8px 20px', backgroundColor: '#fff', border: '1px solid #ccc', borderBottom: 'none', borderRadius: '4px 4px 0 0', fontSize: '13px', fontWeight: 'bold' }}>RC section</div>
                <div style={{ padding: '8px 20px', backgroundColor: '#e0e0e0', border: '1px solid #ccc', borderBottom: 'none', borderRadius: '4px 4px 0 0', fontSize: '13px', color: '#666' }}>Tab2</div>
            </div>

            {/* Main Content Area */}
            <div style={{ flex: 1, backgroundColor: '#fff', borderTop: '1px solid #ccc', padding: '20px', overflowY: 'auto' }}>
                <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '30px' }}>

                    {/* Design Standard Section */}
                    <section>
                        <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>Design Standard</h2>
                        <div style={{ marginBottom: '10px' }}>
                            <select
                                value={designStandard}
                                onChange={(e) => setDesignStandard(e.target.value)}
                                style={{
                                    padding: '8px 12px',
                                    border: '1px solid #ccc',
                                    borderRadius: '4px',
                                    fontSize: '14px',
                                    width: '400px',
                                    backgroundColor: '#fff',
                                    cursor: 'pointer'
                                }}
                            >
                                <option value="강도설계법(도로교 설계기준, 2010)">강도설계법(도로교 설계기준, 2010)</option>
                                <option value="강도설계법(콘크리트구조 설계기준, 2021)">강도설계법(콘크리트구조 설계기준, 2021)</option>
                                <option value="한계상태설계법(도로교 설계기준, 2015)">한계상태설계법(도로교 설계기준, 2015)</option>
                            </select>
                        </div>
                    </section>

                    {/* Material Section */}
                    <section>
                        <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>Material</h2>
                        <table style={{ borderCollapse: 'collapse', fontSize: '13px', textAlign: 'center' }}>
                            <thead>
                                <tr>
                                    <th style={{ border: '1px solid #ccc', backgroundColor: '#f8f8f8', padding: '8px 20px', color: '#666', minWidth: '100px' }}>fck(MPa)</th>
                                    <th style={{ border: '1px solid #ccc', backgroundColor: '#f8f8f8', padding: '8px 20px', color: '#666', minWidth: '100px' }}>fy(MPa)</th>
                                    <th style={{ border: '1px solid #ccc', backgroundColor: '#f8f8f8', padding: '8px 20px', color: '#666', minWidth: '100px' }}>Øf</th>
                                    <th style={{ border: '1px solid #ccc', backgroundColor: '#f8f8f8', padding: '8px 20px', color: '#666', minWidth: '100px' }}>Øv</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td style={{ border: '1px solid #ccc', padding: '0' }}><input type="text" value={material.fck} onChange={(e) => handleMaterialChange(e, 'fck')} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none' }} /></td>
                                    <td style={{ border: '1px solid #ccc', padding: '0' }}><input type="text" value={material.fy} onChange={(e) => handleMaterialChange(e, 'fy')} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none' }} /></td>
                                    <td style={{ border: '1px solid #ccc', padding: '0', backgroundColor: '#f5f5f5' }}><input type="text" value={material.phi_f} readOnly style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent', color: '#666' }} /></td>
                                    <td style={{ border: '1px solid #ccc', padding: '0', backgroundColor: '#f5f5f5' }}><input type="text" value={material.phi_v} readOnly style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent', color: '#666' }} /></td>
                                </tr>
                            </tbody>
                        </table>
                    </section>

                    {/* Main Analysis Sections */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
                        
                        {/* 1. Force & Section Section */}
                        <section>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ backgroundColor: '#3b82f6', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>1</span>
                                단면 및 하중 (Force & Section)
                            </h2>
                            <div style={{ border: '1px solid #ccc', borderRadius: '4px', overflow: 'auto', backgroundColor: '#fff' }}>
                                <table style={{ borderCollapse: 'collapse', fontSize: '12px', width: '100%', minWidth: '900px' }}>
                                    <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
                                        <tr style={{ backgroundColor: '#f2f2f2' }}>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '30px' }}>
                                                <input type="checkbox" checked={selectAll} onChange={handleToggleSelectAll} style={{ cursor: 'pointer' }} />
                                            </th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '40px' }}>No</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '120px' }}>Name</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>H<br />(mm)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>B<br />(mm)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Mu<br />(kN.m)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Vu<br />(kN)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Nu<br />(kN)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Ms<br />(kN.m)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '130px' }}>환경조건</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows.map((row, idx) => (
                                            <tr key={row.id} style={{ backgroundColor: row.selected ? '#eff6ff' : (idx % 2 === 0 ? '#fff' : '#fcfcfc') }}>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center' }}>
                                                    <input type="checkbox" checked={row.selected} onChange={() => handleToggleSelect(idx)} style={{ cursor: 'pointer' }} />
                                                </td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f2f2f2', fontWeight: 'bold', color: '#666' }}>{row.id}</td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.name} onChange={(e) => handleRowChange(e, idx, 'name')} onKeyDown={(e) => handleKeyDown(e, idx, 0)} onFocus={handleFocus} data-row={idx} data-col={0} style={{ width: '100%', height: '35px', padding: '0 8px', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.H} onChange={(e) => handleRowChange(e, idx, 'H')} onKeyDown={(e) => handleKeyDown(e, idx, 1)} onFocus={handleFocus} data-row={idx} data-col={1} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.B} onChange={(e) => handleRowChange(e, idx, 'B')} onKeyDown={(e) => handleKeyDown(e, idx, 2)} onFocus={handleFocus} data-row={idx} data-col={2} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Mu} onChange={(e) => handleRowChange(e, idx, 'Mu')} onKeyDown={(e) => handleKeyDown(e, idx, 3)} onFocus={handleFocus} data-row={idx} data-col={3} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Vu} onChange={(e) => handleRowChange(e, idx, 'Vu')} onKeyDown={(e) => handleKeyDown(e, idx, 4)} onFocus={handleFocus} data-row={idx} data-col={4} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Nu} onChange={(e) => handleRowChange(e, idx, 'Nu')} onKeyDown={(e) => handleKeyDown(e, idx, 5)} onFocus={handleFocus} data-row={idx} data-col={5} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Ms} onChange={(e) => handleRowChange(e, idx, 'Ms')} onKeyDown={(e) => handleKeyDown(e, idx, 6)} onFocus={handleFocus} data-row={idx} data-col={6} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                    <select value={row.crack_case} onChange={(e) => handleRowChange(e, idx, 'crack_case')} onKeyDown={(e) => handleKeyDown(e, idx, 7)} onFocus={handleSelectFocus} data-row={idx} data-col={7} style={{ width: '100%', height: '35px', border: 'none', outline: 'none', backgroundColor: 'transparent', textAlignLast: 'center', cursor: 'pointer', fontSize: '11px' }}>
                                                        <option value="건조한 환경">건조한 환경</option>
                                                        <option value="일반환경">일반환경</option>
                                                        <option value="부식성 환경">부식성 환경</option>
                                                        <option value="극심한 부식성 환경">극심한 부식성 환경</option>
                                                    </select>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {/* 2. Rebar Detail Section */}
                        <section>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ backgroundColor: '#10b981', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>2</span>
                                철근 상세 (Rebar Detail)
                            </h2>
                            <div style={{ border: '1px solid #ccc', borderRadius: '4px', overflow: 'auto', backgroundColor: '#fff' }}>
                                <table style={{ borderCollapse: 'collapse', fontSize: '12px', width: '100%', minWidth: '1200px' }}>
                                    <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
                                        <tr style={{ backgroundColor: '#f2f2f2' }}>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '40px' }} rowSpan={2}>No</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '120px' }} rowSpan={2}>Name</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', backgroundColor: '#eff6ff' }} colSpan={3}>1단 (Layer 1)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', backgroundColor: '#f0fdf4' }} colSpan={3}>2단 (Layer 2)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', backgroundColor: '#fff7ed' }} colSpan={3}>3단 (Layer 3)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', backgroundColor: '#f5f5f5' }} colSpan={3}>전단 (Stirrup)</th>
                                        </tr>
                                        <tr style={{ backgroundColor: '#f9f9f9' }}>
                                            {/* Layer 1 */}
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>dc1</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '60px' }}>Dia</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>Num</th>
                                            {/* Layer 2 */}
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>dc2</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '60px' }}>Dia</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>Num</th>
                                            {/* Layer 3 */}
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>dc3</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '60px' }}>Dia</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>Num</th>
                                            {/* Stirrup */}
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '60px' }}>Dia</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>Leg</th>
                                            <th style={{ border: '1px solid #ddd', padding: '4px', fontSize: '10px', minWidth: '50px' }}>Space</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows.map((row, idx) => (
                                            <tr key={row.id} style={{ backgroundColor: row.selected ? '#eff6ff' : (idx % 2 === 0 ? '#fff' : '#fcfcfc') }}>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f2f2f2', fontWeight: 'bold', color: '#666' }}>{row.id}</td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.name} readOnly style={{ width: '100%', height: '35px', padding: '0 8px', border: 'none', outline: 'none', backgroundColor: 'transparent', color: '#666' }} /></td>
                                                
                                                {/* Layer 1 */}
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.dc1} onChange={(e) => handleRowChange(e, idx, 'dc1')} onKeyDown={(e) => handleKeyDown(e, idx, 8)} onFocus={handleFocus} data-row={idx} data-col={8} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                    <select value={row.dia1} onChange={(e) => handleRowChange(e, idx, 'dia1')} onKeyDown={(e) => handleKeyDown(e, idx, 9)} onFocus={handleSelectFocus} data-row={idx} data-col={9} style={{ width: '100%', height: '35px', border: 'none' }}>
                                                        {[10, 13, 16, 19, 22, 25, 29, 32, 35].map(d => <option key={d} value={d}>{d}</option>)}
                                                    </select>
                                                </td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.num1} onChange={(e) => handleRowChange(e, idx, 'num1')} onKeyDown={(e) => handleKeyDown(e, idx, 10)} onFocus={handleFocus} data-row={idx} data-col={10} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>

                                                {/* Layer 2 */}
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.dc2} onChange={(e) => handleRowChange(e, idx, 'dc2')} onKeyDown={(e) => handleKeyDown(e, idx, 11)} onFocus={handleFocus} data-row={idx} data-col={11} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                    <select value={row.dia2} onChange={(e) => handleRowChange(e, idx, 'dia2')} onKeyDown={(e) => handleKeyDown(e, idx, 12)} onFocus={handleSelectFocus} data-row={idx} data-col={12} style={{ width: '100%', height: '35px', border: 'none' }}>
                                                        <option value={0}>철근없음</option>
                                                        {[10, 13, 16, 19, 22, 25, 29, 32, 35].map(d => <option key={d} value={d}>{d}</option>)}
                                                    </select>
                                                </td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.num2} onChange={(e) => handleRowChange(e, idx, 'num2')} onKeyDown={(e) => handleKeyDown(e, idx, 13)} onFocus={handleFocus} data-row={idx} data-col={13} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>

                                                {/* Layer 3 */}
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.dc3} onChange={(e) => handleRowChange(e, idx, 'dc3')} onKeyDown={(e) => handleKeyDown(e, idx, 14)} onFocus={handleFocus} data-row={idx} data-col={14} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                    <select value={row.dia3} onChange={(e) => handleRowChange(e, idx, 'dia3')} onKeyDown={(e) => handleKeyDown(e, idx, 15)} onFocus={handleSelectFocus} data-row={idx} data-col={15} style={{ width: '100%', height: '35px', border: 'none' }}>
                                                        <option value={0}>철근없음</option>
                                                        {[10, 13, 16, 19, 22, 25, 29, 32, 35].map(d => <option key={d} value={d}>{d}</option>)}
                                                    </select>
                                                </td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.num3} onChange={(e) => handleRowChange(e, idx, 'num3')} onKeyDown={(e) => handleKeyDown(e, idx, 16)} onFocus={handleFocus} data-row={idx} data-col={16} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>

                                                {/* Stirrup */}
                                                <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                    <select value={row.av_dia} onChange={(e) => handleRowChange(e, idx, 'av_dia')} onKeyDown={(e) => handleKeyDown(e, idx, 17)} onFocus={handleSelectFocus} data-row={idx} data-col={17} style={{ width: '100%', height: '35px', border: 'none' }}>
                                                        <option value={0}>철근없음</option>
                                                        {[10, 13, 16, 19, 22, 25, 29, 32, 35, 38, 41, 51].map(d => <option key={d} value={d}>{d}</option>)}
                                                    </select>
                                                </td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.av_leg} onChange={(e) => handleRowChange(e, idx, 'av_leg')} onKeyDown={(e) => handleKeyDown(e, idx, 18)} onFocus={handleFocus} data-row={idx} data-col={18} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>
                                                <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.av_space} onChange={(e) => handleRowChange(e, idx, 'av_space')} onKeyDown={(e) => handleKeyDown(e, idx, 19)} onFocus={handleFocus} data-row={idx} data-col={19} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none' }} /></td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {/* 3. Results Section */}
                        <section>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ backgroundColor: '#f59e0b', color: '#fff', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>3</span>
                                검토 결과 (Results)
                            </h2>
                            <div style={{ border: '1px solid #ccc', borderRadius: '4px', overflow: 'auto', backgroundColor: '#fff' }}>
                                <table style={{ borderCollapse: 'collapse', fontSize: '12px', width: '100%', minWidth: '900px' }}>
                                    <thead>
                                        <tr style={{ backgroundColor: '#f2f2f2' }}>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '40px' }}>No</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '120px' }}>Name</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '100px', backgroundColor: '#f9f9f9' }}>As_req<br />(mm²)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '100px', backgroundColor: '#f9f9f9' }}>As_used<br />(mm²)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '100px', backgroundColor: '#f9f9f9' }}>Ratio<br />(U/R)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '100px', backgroundColor: '#fff7ed' }}>Mr<br />(kN.m)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '80px', backgroundColor: '#fff7ed' }}>안전율<br />(휨)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '80px', backgroundColor: '#f0fdf4' }}>전단보강<br />판정</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '100px', backgroundColor: '#f0fdf4' }}>Vn<br />(kN)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '80px', backgroundColor: '#f0fdf4' }}>안전율<br />(전단)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '80px', backgroundColor: '#fcfcfc' }}>fs<br />(MPa)</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '80px', backgroundColor: '#fcfcfc' }}>균열<br />상태</th>
                                            <th style={{ border: '1px solid #ddd', padding: '8px', width: '60px' }}>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {rows.map((row, idx) => (
                                            <tr key={row.id} style={{ backgroundColor: row.selected ? '#eff6ff' : (idx % 2 === 0 ? '#fff' : '#fcfcfc') }}>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f2f2f2', fontWeight: 'bold', color: '#666' }}>{row.id}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', color: '#666' }}>{row.name}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f9fafb', fontWeight: 'bold' }}>{row.as_req || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f9fafb', fontWeight: 'bold' }}>{row.as_used || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f9fafb', fontWeight: 'bold', color: row.as_ratio > 1 ? '#cc0000' : '#009900' }}>{row.as_ratio || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#fff7ed', color: '#c2410c' }}>{row.Mr || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#fff7ed', color: (row as any).Mr_rate < 1 ? '#cc0000' : '#15803d', fontWeight: 'bold' }}>{(row as any).Mr_rate || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f0fdf4', color: (row as any).V_reinf === '필요' ? '#cc0000' : '#15803d', fontWeight: 'bold' }}>{(row as any).V_reinf || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#15803d' }}>{(row as any).Vn || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f0fdf4', color: (row as any).Vn_rate < 1 ? '#cc0000' : '#15803d', fontWeight: 'bold' }}>{(row as any).Vn_rate || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#fcfcfc', color: '#15803d' }}>{row.fs || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#fcfcfc', color: (row as any).crack_status === 'NG' ? '#cc0000' : '#15803d', fontWeight: 'bold' }}>{(row as any).crack_status || ""}</td>
                                                <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center' }}>
                                                    {row.is_calculating ? <span style={{ color: '#3b82f6' }}>...</span> : (row.is_calculated ? <span style={{ color: '#16a34a' }}>✓</span> : "")}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>

                        {/* Row Control Buttons */}
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <button onClick={handleAddRow} style={{ padding: '8px 20px', backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px', fontSize: '13px', cursor: 'pointer', fontWeight: 'bold' }}>+ 행 추가</button>
                            <button onClick={handleDeleteRow} style={{ padding: '8px 20px', backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px', fontSize: '13px', cursor: 'pointer', color: '#cc0000' }}>- 선택 삭제</button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Modal for Calculation View */}
            {isReportModalOpen && reportData && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
                    backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
                }}>
                    <div style={{
                        backgroundColor: '#fff', width: '90%', maxWidth: '900px', height: '85%',
                        borderRadius: '8px', display: 'flex', flexDirection: 'column', overflow: 'hidden',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.2)'
                    }}>
                        {/* Modal Header */}
                        <div style={{ padding: '15px 20px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>계산과정 - {viewingRowName}</h3>
                            <button onClick={() => setIsReportModalOpen(false)} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer', color: '#666' }}>×</button>
                        </div>

                        {/* Tabs */}
                        <div style={{ padding: '10px 20px', borderBottom: '1px solid #eee', display: 'flex', gap: '5px' }}>
                            {[
                                { id: 'total', label: '전체' },
                                { id: 'flexure', label: '휨모멘트' },
                                { id: 'shear', label: '전단력' },
                                { id: 'service', label: '사용성' }
                            ].map(tab => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveReportTab(tab.id)}
                                    style={{
                                        padding: '8px 20px',
                                        backgroundColor: activeReportTab === tab.id ? '#fff' : '#f5f5f5',
                                        border: '1px solid #ccc',
                                        borderBottom: activeReportTab === tab.id ? '2px solid #0066cc' : '1px solid #ccc',
                                        borderRadius: '4px 4px 0 0',
                                        cursor: 'pointer',
                                        fontSize: '13px',
                                        fontWeight: activeReportTab === tab.id ? 'bold' : 'normal',
                                        color: activeReportTab === tab.id ? '#0066cc' : '#666'
                                    }}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>

                        {/* Text Content */}
                        <div style={{ flex: 1, padding: '20px', paddingRight: '10px', overflowY: 'auto', backgroundColor: '#fcfcfc' }}>
                            <pre style={{
                                margin: 0, padding: '20px', backgroundColor: '#fff', border: '1px solid #ddd',
                                fontFamily: '"Courier New", Courier, monospace', fontSize: '12px', lineHeight: '1.5',
                                whiteSpace: 'pre-wrap', color: '#333'
                            }}>
                                {reportData[activeReportTab]}
                            </pre>
                        </div>

                        {/* Modal Footer */}
                        <div style={{ padding: '15px 20px', borderTop: '1px solid #eee', display: 'flex', justifyContent: 'flex-start', gap: '10px' }}>
                            <button onClick={copyToClipboard} style={{ padding: '8px 20px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#fff', cursor: 'pointer', fontSize: '13px' }}>복사</button>
                            <button onClick={saveToTextFile} style={{ padding: '8px 20px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#fff', cursor: 'pointer', fontSize: '13px' }}>텍스트 저장</button>
                            <button onClick={() => setIsReportModalOpen(false)} style={{ padding: '8px 20px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#fff', cursor: 'pointer', fontSize: '13px' }}>닫기</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Footer / Status Bar Area */}
            <div style={{ backgroundColor: '#f0f0f0', borderTop: '1px solid #ccc', padding: '5px 15px', fontSize: '11px', color: '#666', display: 'flex', justifyContent: 'space-between' }}>
                <Link href="/dashboard" style={{ color: '#0066cc', textDecoration: 'none' }}>← 대시보드로 돌아가기</Link>
                <span>Ready</span>
            </div>
        </main>
    );
}
