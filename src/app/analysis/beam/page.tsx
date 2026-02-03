"use client";

import { useState } from "react";
import Link from "next/link";

export default function RCBeamAnalysisPage() {
    const [material, setMaterial] = useState({
        fck: 35,
        fy: 400,
        phi_f: 0.85,
        phi_v: 0.85
    });

    const [rows, setRows] = useState([
        {
            id: 1,
            name: "Center",
            Mu: 1000,
            Vu: 50,
            Nu: 5,
            Ms: 80,
            H: 800,
            B: 1000,
            Dc: 80,
            as_dia: 25,
            as_num: 8,
            av_dia: 16,
            av_leg: 2,
            av_space: 400,
            as_req: 0,
            as_used: 0,
            as_ratio: 0,
            is_calculating: false,
            selected: false
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
                H: 0, B: 0, Dc: 80,
                as_dia: 13,
                as_num: 0,
                av_dia: 16,
                av_leg: 0,
                av_space: 200,
                as_req: 0,
                as_used: 0,
                as_ratio: 0,
                is_calculating: false,
                selected: false
            }
        ]);
    };

    const handleDeleteRow = () => {
        const remainingRows = rows.filter(row => !row.selected);
        if (remainingRows.length === 0 && rows.length > 0) {
            // Keep at least one empty row if everything is deleted
            setRows([{
                id: 1, name: "", Mu: 0, Vu: 0, Nu: 0, Ms: 0, H: 0, B: 0, Dc: 80,
                as_dia: 13, as_num: 0, av_dia: 16, av_leg: 0, av_space: 200,
                as_req: 0, as_used: 0, as_ratio: 0, is_calculating: false, selected: false
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
    };

    const handleRowChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>, index: number, key: string) => {
        let value: string | number;
        if (key === 'name') {
            value = e.target.value;
        } else {
            const val = e.target.value;
            // Allow empty string or just a minus sign for better typing experience
            if (val === "" || val === "-") {
                value = val;
            } else {
                value = e.target.tagName === 'SELECT' ? parseInt(val) : (parseFloat(val) || 0);
            }
        }

        const newRows = [...rows];
        (newRows[index] as any)[key] = value;
        setRows(newRows);
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

        try {
            const response = await fetch('/api/analysis/beam', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ material, rows: validRows })
            });

            if (response.ok) {
                const results = await response.json();
                const newRows = [...rows];

                // Update Material phi values from the first valid result if available
                if (results.length > 0 && !results[0].error) {
                    setMaterial(prev => ({
                        ...prev,
                        phi_f: results[0].phi_f,
                        phi_v: results[0].phi_v
                    }));
                }

                // Map results back to rows
                let resultIdx = 0;
                newRows.forEach((row, i) => {
                    if (row.H > 0 && row.B > 0) {
                        const res = results[resultIdx++];
                        if (res) {
                            (row as any).as_req = res.as_req;
                            (row as any).as_used = res.as_used;
                            (row as any).as_ratio = res.as_ratio;
                            (row as any).Mr = res.Mr;
                            (row as any).fs = res.fs;
                        }
                    }
                });
                setRows(newRows);
            } else {
                alert("Calculation failed. Please check your inputs.");
            }
        } catch (error) {
            console.error("Calculation Error:", error);
            alert("An error occurred during calculation.");
        }
    };

    const handleExport = async () => {
        const selectedRows = rows.filter(row => row.selected);
        if (selectedRows.length === 0) {
            alert("엑셀로 내보낼 행을 먼저 선택해주세요.");
            return;
        }

        try {
            const response = await fetch("/api/analysis/beam/export", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ material, rows: selectedRows })
            });

            if (!response.ok) throw new Error("Export failed");

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `RC_Beam_Report_${new Date().getTime()}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error("Export Error:", error);
            alert("엑셀 내보내기 중 오류가 발생했습니다.");
        }
    };

    const toolbarButtons = [
        { label: "Calc", icon: "📊", onClick: handleCalculate },
        { label: "Export", icon: "📄", onClick: handleExport },
        { label: "View", icon: "👁️", onClick: () => alert("View mode not implemented yet") }
    ];

    return (
        <main style={{ minHeight: '100vh', backgroundColor: '#f0f0f0', color: '#333', display: 'flex', flexDirection: 'column' }}>
            {/* Top Menu Bar */}
            <div style={{ backgroundColor: '#fff', borderBottom: '1px solid #ccc', padding: '2px 10px', display: 'flex', gap: '20px', fontSize: '12px' }}>
                {["파일", "Calc", "View", "도움말"].map(item => (
                    <span key={item} style={{ cursor: 'pointer', padding: '2px 5px' }}>{item}</span>
                ))}
            </div>

            {/* Toolbar */}
            <div style={{ backgroundColor: '#f5f5f5', borderBottom: '1px solid #ccc', padding: '5px 10px', display: 'flex', gap: '10px' }}>
                {toolbarButtons.map(btn => (
                    <button
                        key={btn.label}
                        onClick={btn.onClick}
                        style={{ display: 'flex', alignItems: 'center', gap: '5px', padding: '4px 12px', backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '4px', fontSize: '13px', cursor: 'pointer', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}
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

                    {/* Force & Rebar Area Section */}
                    <section style={{ overflowX: 'auto' }}>
                        <h2 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>Force & Rebar Area</h2>
                        <div style={{ border: '1px solid #ccc', borderRadius: '4px', maxHeight: '600px', overflowY: 'auto', overflowX: 'auto' }}>
                            <table style={{ borderCollapse: 'collapse', fontSize: '12px', minWidth: '1800px' }}>
                                <thead style={{ position: 'sticky', top: 0, zIndex: 20 }}>
                                    <tr style={{ backgroundColor: '#f2f2f2' }}>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', width: '30px' }}>
                                            <input type="checkbox" checked={selectAll} onChange={handleToggleSelectAll} style={{ cursor: 'pointer' }} />
                                        </th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', width: '40px' }}>No</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '120px' }}>Name</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Mu<br />(kN.m)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Vu<br />(kN)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Nu<br />(kN)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Ms<br />(kN.m)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>H<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>B<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Dc<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px' }}>As_Dia<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>As_Num<br />(EA)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px' }}>Av_Dia<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '80px' }}>Av_Leg<br />(EA)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px' }}>Av_Space<br />(mm)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px', backgroundColor: '#f9f9f9' }}>As_req<br />(mm²)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px', backgroundColor: '#f9f9f9' }}>As_used<br />(mm²)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px', backgroundColor: '#f9f9f9' }}>Ratio<br />(U/R)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px', backgroundColor: '#fff7ed' }}>Mr<br />(kN.m)</th>
                                        <th style={{ border: '1px solid #ddd', padding: '8px', minWidth: '100px', backgroundColor: '#f0fdf4' }}>fs<br />(MPa)</th>
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
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Mu} onChange={(e) => handleRowChange(e, idx, 'Mu')} onKeyDown={(e) => handleKeyDown(e, idx, 1)} onFocus={handleFocus} data-row={idx} data-col={1} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Vu} onChange={(e) => handleRowChange(e, idx, 'Vu')} onKeyDown={(e) => handleKeyDown(e, idx, 2)} onFocus={handleFocus} data-row={idx} data-col={2} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Nu} onChange={(e) => handleRowChange(e, idx, 'Nu')} onKeyDown={(e) => handleKeyDown(e, idx, 3)} onFocus={handleFocus} data-row={idx} data-col={3} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Ms} onChange={(e) => handleRowChange(e, idx, 'Ms')} onKeyDown={(e) => handleKeyDown(e, idx, 4)} onFocus={handleFocus} data-row={idx} data-col={4} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.H} onChange={(e) => handleRowChange(e, idx, 'H')} onKeyDown={(e) => handleKeyDown(e, idx, 5)} onFocus={handleFocus} data-row={idx} data-col={5} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.B} onChange={(e) => handleRowChange(e, idx, 'B')} onKeyDown={(e) => handleKeyDown(e, idx, 6)} onFocus={handleFocus} data-row={idx} data-col={6} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.Dc} onChange={(e) => handleRowChange(e, idx, 'Dc')} onKeyDown={(e) => handleKeyDown(e, idx, 7)} onFocus={handleFocus} data-row={idx} data-col={7} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                <select value={row.as_dia} onChange={(e) => handleRowChange(e, idx, 'as_dia')} onKeyDown={(e) => handleKeyDown(e, idx, 8)} onFocus={handleSelectFocus} data-row={idx} data-col={8} style={{ width: '100%', height: '35px', border: 'none', outline: 'none', backgroundColor: 'transparent', textAlignLast: 'center', cursor: 'pointer' }}>
                                                    <option value="10">10</option>
                                                    <option value="13">13</option>
                                                    <option value="16">16</option>
                                                    <option value="19">19</option>
                                                    <option value="22">22</option>
                                                    <option value="25">25</option>
                                                    <option value="29">29</option>
                                                    <option value="32">32</option>
                                                    <option value="35">35</option>
                                                </select>
                                            </td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.as_num} onChange={(e) => handleRowChange(e, idx, 'as_num')} onKeyDown={(e) => handleKeyDown(e, idx, 9)} onFocus={handleFocus} data-row={idx} data-col={9} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}>
                                                <select value={row.av_dia} onChange={(e) => handleRowChange(e, idx, 'av_dia')} onKeyDown={(e) => handleKeyDown(e, idx, 10)} onFocus={handleSelectFocus} data-row={idx} data-col={10} style={{ width: '100%', height: '35px', border: 'none', outline: 'none', backgroundColor: 'transparent', textAlignLast: 'center', cursor: 'pointer' }}>
                                                    <option value="10">10</option>
                                                    <option value="13">13</option>
                                                    <option value="16">16</option>
                                                    <option value="19">19</option>
                                                    <option value="22">22</option>
                                                    <option value="25">25</option>
                                                    <option value="29">29</option>
                                                    <option value="32">32</option>
                                                    <option value="35">35</option>
                                                    <option value="38">38</option>
                                                    <option value="41">41</option>
                                                    <option value="51">51</option>
                                                </select>
                                            </td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.av_leg} onChange={(e) => handleRowChange(e, idx, 'av_leg')} onKeyDown={(e) => handleKeyDown(e, idx, 11)} onFocus={handleFocus} data-row={idx} data-col={11} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '0' }}><input type="text" value={row.av_space} onChange={(e) => handleRowChange(e, idx, 'av_space')} onKeyDown={(e) => handleKeyDown(e, idx, 12)} onFocus={handleFocus} data-row={idx} data-col={12} style={{ width: '100%', height: '35px', textAlign: 'center', border: 'none', outline: 'none', backgroundColor: 'transparent' }} /></td>
                                            <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f9fafb', fontWeight: 'bold', color: '#0066cc' }}>{(row as any).as_req || ""}</td>
                                            <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f9fafb', fontWeight: 'bold' }}>{(row as any).as_used || ""}</td>
                                            <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'center', backgroundColor: '#f9fafb', fontWeight: 'bold', color: (row as any).as_ratio > 1 ? '#cc0000' : '#009900' }}>{(row as any).as_ratio || ""}</td>
                                            <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#fff7ed', color: '#c2410c' }}>{(row as any).Mr || ""}</td>
                                            <td style={{ border: '1px solid #eee', padding: '8px', textAlign: 'right', backgroundColor: '#f0fdf4', color: '#15803d' }}>{(row as any).fs || ""}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Row Control Buttons */}
                        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                            <button
                                onClick={handleAddRow}
                                style={{ padding: '6px 15px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '4px', fontSize: '13px', color: '#16a34a', cursor: 'pointer', fontWeight: 'bold' }}
                            >
                                + Add Row
                            </button>
                            <button
                                onClick={handleDeleteRow}
                                style={{
                                    padding: '6px 15px',
                                    backgroundColor: rows.some(r => r.selected) ? '#fee2e2' : '#fef2f2',
                                    border: rows.some(r => r.selected) ? '1px solid #ef4444' : '1px solid #fecaca',
                                    borderRadius: '4px',
                                    fontSize: '13px',
                                    color: rows.some(r => r.selected) ? '#b91c1c' : '#dc2626',
                                    cursor: 'pointer',
                                    fontWeight: 'bold'
                                }}
                            >
                                - Delete Selected Rows
                            </button>
                        </div>
                    </section>
                </div>
            </div>

            {/* Footer / Status Bar Area */}
            <div style={{ backgroundColor: '#f0f0f0', borderTop: '1px solid #ccc', padding: '5px 15px', fontSize: '11px', color: '#666', display: 'flex', justifyContent: 'space-between' }}>
                <Link href="/dashboard" style={{ color: '#0066cc', textDecoration: 'none' }}>← 대시보드로 돌아가기</Link>
                <span>Ready</span>
            </div>
        </main>
    );
}
