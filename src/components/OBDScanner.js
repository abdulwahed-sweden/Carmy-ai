// src/components/OBDScanner.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const OBDScanner = ({ carId }) => {
    const [device, setDevice] = useState(null);
    const [connected, setConnected] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [codes, setCodes] = useState([]);
    const [diagnosticResults, setDiagnosticResults] = useState(null);
    const [error, setError] = useState(null);
    
    const connectToDevice = async () => {
        try {
            // طلب الجهاز عبر Bluetooth
            const device = await navigator.bluetooth.requestDevice({
                filters: [
                    { services: ['0000fff0-0000-1000-8000-00805f9b34fb'] }, // خدمة OBD-II النموذجية
                    { namePrefix: 'OBDII' },
                    { namePrefix: 'ELM327' }
                ],
                optionalServices: ['0000fff0-0000-1000-8000-00805f9b34fb']
            });
            
            setDevice(device);
            
            // الاستماع إلى حدث الاتصال
            device.addEventListener('gattserverdisconnected', () => {
                setConnected(false);
                setError('تم قطع الاتصال بالجهاز');
            });
            
            // إنشاء اتصال GATT
            const server = await device.gatt.connect();
            const service = await server.getPrimaryService('0000fff0-0000-1000-8000-00805f9b34fb');
            
            // الحصول على خصائص الإرسال والاستقبال
            const txCharacteristic = await service.getCharacteristic('0000fff1-0000-1000-8000-00805f9b34fb');
            const rxCharacteristic = await service.getCharacteristic('0000fff2-0000-1000-8000-00805f9b34fb');
            
            // الاستماع للبيانات الواردة
            await rxCharacteristic.startNotifications();
            rxCharacteristic.addEventListener('characteristicvaluechanged', handleNotifications);
            
            setConnected(true);
            setError(null);
            
            return { txCharacteristic, rxCharacteristic };
        } catch (error) {
            console.error('خطأ في الاتصال بالجهاز:', error);
            setError('فشل الاتصال بالجهاز: ' + error.message);
            return null;
        }
    };
    
    // معالجة البيانات الواردة من الجهاز
    const handleNotifications = (event) => {
        const value = event.target.value;
        const decoder = new TextDecoder('utf-8');
        const data = decoder.decode(value);
        
        // تحليل البيانات للحصول على أكواد الأعطال
        parseOBDData(data);
    };
    
    // تحليل بيانات OBD للحصول على أكواد الأعطال
    const parseOBDData = (data) => {
        // مثال لتحليل بيانات OBD-II
        // هذا مجرد مثال وقد يحتاج إلى تعديل حسب الجهاز المستخدم
        const lines = data.split('\r\n');
        
        lines.forEach(line => {
            if (line.includes('43') && line.length > 2) {
                // 43 هو رمز الاستجابة لقراءة أكواد الأعطال
                const parts = line.trim().split(' ').filter(part => part);
                parts.shift(); // إزالة "43"
                
                for (let i = 0; i < parts.length; i += 2) {
                    if (i + 1 < parts.length) {
                        const codeType = parseInt(parts[i].charAt(0), 16);
                        if (codeType < 4) { // التحقق من أن القيمة صالحة
                            let codeChar;
                            switch (codeType) {
                                case 0: codeChar = 'P'; break;
                                case 1: codeChar = 'C'; break;
                                case 2: codeChar = 'B'; break;
                                case 3: codeChar = 'U'; break;
                                default: codeChar = 'P';
                            }
                            
                            const codeValue = parts[i].substring(1) + parts[i + 1];
                            const dtcCode = `${codeChar}${codeValue}`;
                            
                            // إضافة الكود إلى القائمة إذا لم يكن موجودًا
                            setCodes(prevCodes => {
                                if (!prevCodes.includes(dtcCode)) {
                                    return [...prevCodes, dtcCode];
                                }
                                return prevCodes;
                            });
                        }
                    }
                }
            }
        });
    };
    
    // بدء فحص أكواد الأعطال
    const startScan = async () => {
        try {
            setScanning(true);
            setCodes([]);
            
            if (!connected || !device) {
                const connection = await connectToDevice();
                if (!connection) {
                    setScanning(false);
                    return;
                }
                
                const { txCharacteristic } = connection;
                
                // إرسال أوامر لقراءة أكواد الأعطال
                const encoder = new TextEncoder();
                await txCharacteristic.writeValue(encoder.encode('ATZ\r')); // إعادة ضبط
                await new Promise(resolve => setTimeout(resolve, 1000));
                await txCharacteristic.writeValue(encoder.encode('ATE0\r')); // إيقاف صدى الأوامر
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('ATL0\r')); // إيقاف خطوط جديدة
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('ATH0\r')); // إيقاف العناوين
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('ATS0\r')); // إيقاف المسافات
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('ATSP0\r')); // تعيين البروتوكول تلقائيًا
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('0101\r')); // التحقق من الاتصال
                await new Promise(resolve => setTimeout(resolve, 300));
                await txCharacteristic.writeValue(encoder.encode('03\r')); // قراءة أكواد الأعطال
                
                // إيقاف المسح بعد 10 ثوانٍ
                setTimeout(() => {
                    setScanning(false);
                    if (codes.length > 0 && carId) {
                        sendCodesToServer();
                    }
                }, 10000);
            }
        } catch (error) {
            console.error('خطأ في الفحص:', error);
            setError('فشل الفحص: ' + error.message);
            setScanning(false);
        }
    };
    
    // إرسال الأكواد إلى الخادم للتحليل
    const sendCodesToServer = async () => {
        try {
            const response = await axios.post('/api/diagnostics/obd-data/', {
                car_id: carId,
                obd_codes: codes
            });
            
            setDiagnosticResults(response.data);
        } catch (error) {
            console.error('خطأ في إرسال البيانات للخادم:', error);
            setError('فشل تحليل الأكواد: ' + (error.response?.data?.error || error.message));
        }
    };
    
    // قطع الاتصال بالجهاز
    const disconnect = () => {
        if (device && device.gatt.connected) {
            device.gatt.disconnect();
        }
        setConnected(false);
        setDevice(null);
    };
    
    return (
        <div className="card shadow">
            <div className="card-header bg-primary text-white">
                <h3 className="mb-0">ماسح أكواد الأعطال (OBD-II)</h3>
            </div>
            <div className="card-body">
                {!connected ? (
                    <div className="d-grid gap-2">
                        <button 
                            className="btn btn-lg btn-primary" 
                            onClick={connectToDevice}
                            disabled={scanning}
                        >
                            <i className="bi bi-bluetooth me-2"></i>
                            الاتصال بجهاز OBD-II
                        </button>
                        <p className="text-muted mt-2">
                            قم بتشغيل جهاز OBD-II وتأكد من تفعيل البلوتوث على جهازك.
                        </p>
                    </div>
                ) : (
                    <div>
                        <div className="alert alert-success">
                            <i className="bi bi-bluetooth me-2"></i>
                            متصل بجهاز: {device.name || 'جهاز OBD-II'}
                        </div>
                        
                        <div className="d-grid gap-2">
                            {!scanning ? (
                                <button 
                                    className="btn btn-lg btn-success" 
                                    onClick={startScan}
                                >
                                    <i className="bi bi-search me-2"></i>
                                    بدء فحص أكواد الأعطال
                                </button>
                            ) : (
                                <button className="btn btn-lg btn-warning" disabled>
                                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                    جاري الفحص...
                                </button>
                            )}
                            
                            <button 
                                className="btn btn-outline-danger" 
                                onClick={disconnect}
                                disabled={scanning}
                            >
                                <i className="bi bi-x-circle me-2"></i>
                                قطع الاتصال
                            </button>
                        </div>
                        
                        {codes.length > 0 && (
                            <div className="mt-4">
                                <h4>أكواد الأعطال المكتشفة</h4>
                                <div className="d-flex flex-wrap gap-2 mt-2">
                                    {codes.map((code, index) => (
                                        <span key={index} className="badge bg-danger fs-5 p-2">
                                            {code}
                                        </span>
                                    ))}
                                </div>
                                
                                {!scanning && !diagnosticResults && (
                                    <div className="d-grid mt-3">
                                        <button 
                                            className="btn btn-primary"
                                            onClick={sendCodesToServer}
                                            disabled={!carId}
                                        >
                                            تحليل الأكواد
                                        </button>
                                        {!carId && (
                                            <div className="text-danger small mt-1">
                                                يجب تحديد السيارة أولاً للتحليل
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
                
                {error && (
                    <div className="alert alert-danger mt-3">
                        {error}
                    </div>
                )}
                
                {diagnosticResults && (
                    <div className="mt-4">
                        <h4>نتائج التشخيص</h4>
                        <div className="alert alert-info">
                            سيارة: {diagnosticResults.car.brand} {diagnosticResults.car.model} {diagnosticResults.car.year}
                        </div>
                        
                        {diagnosticResults.diagnostics.map((diagnostic, index) => (
                            <div key={index} className="card mb-3">
                                <div className={`card-header ${diagnostic.severity === 'HIGH' ? 'bg-danger' : diagnostic.severity === 'MEDIUM' ? 'bg-warning' : 'bg-info'} text-white`}>
                                    <h5 className="mb-0">{diagnostic.code} - {diagnostic.description}</h5>
                                </div>
                                <div className="card-body">
                                    <p><strong>الفئة:</strong> {diagnostic.category}</p>
                                    
                                    {diagnostic.common_causes && (
                                        <div className="mb-3">
                                            <h6>الأسباب المحتملة:</h6>
                                            <p>{diagnostic.common_causes}</p>
                                        </div>
                                    )}
                                    
                                    {diagnostic.solutions && (
                                        <div className="mb-3">
                                            <h6>الحلول المقترحة:</h6>
                                            <p>{diagnostic.solutions}</p>
                                        </div>
                                    )}
                                    
                                    {diagnostic.emergency_action && (
                                        <div className="alert alert-warning">
                                            <strong>إجراء الطوارئ:</strong> {diagnostic.emergency_action}
                                        </div>
                                    )}
                                    
                                    {diagnostic.note && (
                                        <div className="alert alert-secondary">
                                            {diagnostic.note}
                                        </div>
                                    )}
                                    
                                    {diagnostic.resources && diagnostic.resources.length > 0 && (
                                        <div className="mt-3">
                                            <h6>موارد مفيدة:</h6>
                                            <ul className="list-group">
                                                {diagnostic.resources.map((resource, idx) => (
                                                    <li key={idx} className="list-group-item">
                                                        <a href={resource.url} target="_blank" rel="noopener noreferrer">
                                                            {resource.title} ({resource.type})
                                                        </a>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        
                        {diagnosticResults.missing_codes.length > 0 && (
                            <div className="alert alert-warning">
                                <h6>أكواد غير معروفة:</h6>
                                <p>لم يتم العثور على المعلومات التالية في قاعدة البيانات:</p>
                                <div className="d-flex flex-wrap gap-2 mt-2">
                                    {diagnosticResults.missing_codes.map((code, index) => (
                                        <span key={index} className="badge bg-secondary fs-6 p-2">
                                            {code}
                                        </span>
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

export default OBDScanner;