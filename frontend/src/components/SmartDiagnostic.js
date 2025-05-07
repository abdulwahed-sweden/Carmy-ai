// src/components/SmartDiagnostic.js
import React, { useState } from 'react';
import axios from 'axios';

const SmartDiagnostic = () => {
    const [brand, setBrand] = useState('');
    const [model, setModel] = useState('');
    const [year, setYear] = useState('');
    const [problemDescription, setProblemDescription] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            const response = await axios.post('/api/diagnostics/smart-diagnostic/', {
                brand,
                model,
                year,
                problem_description: problemDescription
            });
            
            setResults(response.data);
        } catch (err) {
            setError('حدث خطأ أثناء تحليل المشكلة. يرجى المحاولة مرة أخرى.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="card shadow">
            <div className="card-header bg-primary text-white">
                <h3 className="mb-0">التشخيص الذكي للأعطال</h3>
            </div>
            <div className="card-body">
                <form onSubmit={handleSubmit}>
                    <div className="row mb-3">
                        <div className="col-md-4">
                            <div className="form-floating">
                                <input
                                    type="text"
                                    className="form-control"
                                    id="brand"
                                    placeholder="الشركة المصنعة"
                                    value={brand}
                                    onChange={(e) => setBrand(e.target.value)}
                                />
                                <label htmlFor="brand">الشركة المصنعة</label>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="form-floating">
                                <input
                                    type="text"
                                    className="form-control"
                                    id="model"
                                    placeholder="الموديل"
                                    value={model}
                                    onChange={(e) => setModel(e.target.value)}
                                />
                                <label htmlFor="model">الموديل</label>
                            </div>
                        </div>
                        <div className="col-md-4">
                            <div className="form-floating">
                                <input
                                    type="number"
                                    className="form-control"
                                    id="year"
                                    placeholder="سنة الصنع"
                                    value={year}
                                    onChange={(e) => setYear(e.target.value)}
                                />
                                <label htmlFor="year">سنة الصنع</label>
                            </div>
                        </div>
                    </div>
                    
                    <div className="form-floating mb-3">
                        <textarea
                            className="form-control"
                            id="problemDescription"
                            placeholder="صف المشكلة التي تواجهها مع سيارتك..."
                            style={{ height: '150px' }}
                            value={problemDescription}
                            onChange={(e) => setProblemDescription(e.target.value)}
                            required
                        ></textarea>
                        <label htmlFor="problemDescription">صف المشكلة التي تواجهها مع سيارتك...</label>
                    </div>
                    
                    <div className="d-grid">
                        <button 
                            type="submit" 
                            className="btn btn-lg btn-primary"
                            disabled={loading || !problemDescription}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                    جاري التحليل...
                                </>
                            ) : 'تحليل المشكلة'}
                        </button>
                    </div>
                </form>
                
                {error && (
                    <div className="alert alert-danger mt-3">
                        {error}
                    </div>
                )}
                
                {results && (
                    <div className="mt-4">
                        <h4>نتائج التشخيص</h4>
                        
                        {results.car && (
                            <div className="alert alert-info">
                                التشخيص لسيارة: {results.car.brand} {results.car.model} {results.car.year}
                            </div>
                        )}
                        
                        <div className="card mb-3">
                            <div className="card-header">
                                <h5 className="mb-0">الأكواد المحتملة</h5>
                            </div>
                            <div className="card-body">
                                {results.possible_codes.length > 0 ? (
                                    <div className="table-responsive">
                                        <table className="table table-striped table-hover">
                                            <thead>
                                                <tr>
                                                    <th>الكود</th>
                                                    <th>الوصف</th>
                                                    <th>الخطورة</th>
                                                    <th>الفئة</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {results.possible_codes.map((code, index) => (
                                                    <tr key={index}>
                                                        <td>
                                                            <a href={`/diagnostics/error-codes/${code.code}`}>
                                                                {code.code}
                                                            </a>
                                                        </td>
                                                        <td>{code.description}</td>
                                                        <td>
                                                            <span className={`badge bg-${code.severity === 'HIGH' ? 'danger' : code.severity === 'MEDIUM' ? 'warning' : 'info'}`}>
                                                                {code.severity === 'HIGH' ? 'عالية' : code.severity === 'MEDIUM' ? 'متوسطة' : 'منخفضة'}
                                                            </span>
                                                        </td>
                                                        <td>{code.category}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                ) : (
                                    <p className="text-muted">لم يتم العثور على أكواد محتملة بناءً على وصف المشكلة.</p>
                                )}
                            </div>
                        </div>
                        
                        {results.car_specific_errors && results.car_specific_errors.length > 0 && (
                            <div className="card">
                                <div className="card-header">
                                    <h5 className="mb-0">تشخيص خاص بسيارتك</h5>
                                </div>
                                <div className="card-body">
                                    {results.car_specific_errors.map((error, index) => (
                                        <div key={index} className="mb-3 p-3 border rounded">
                                            <h5>{error.code} - {error.description}</h5>
                                            <p><strong>الأسباب المحتملة:</strong> {error.common_causes}</p>
                                            {error.solutions && (
                                                <p><strong>الحلول:</strong> {error.solutions}</p>
                                            )}
                                            {error.estimated_cost && (
                                                <p><strong>التكلفة التقديرية:</strong> {error.estimated_cost}</p>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SmartDiagnostic;