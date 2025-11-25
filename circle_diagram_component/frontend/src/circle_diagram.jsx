import React, { useState, useRef, useEffect } from 'react';
import { Streamlit, withStreamlitConnection } from 'streamlit-component-lib';
import './circle_diagram.css';

const CircleDiagram = () => {
  const canvasRef = useRef(null);
  const [clickCount, setClickCount] = useState(0);
  const [showOptionModal, setShowOptionModal] = useState(false);
  const [showDefectModal, setShowDefectModal] = useState(false);
  const [showCavityModal, setShowCavityModal] = useState(false);
  const [pendingClick, setPendingClick] = useState(null);
  const [selectedOption, setSelectedOption] = useState('');
  const [selectedDefect, setSelectedDefect] = useState('');
  const [cavity, setCavity] = useState('');
  const [lastClick, setLastClick] = useState('');

  const defectTypes = [
    "Drop in Mold", "Stains", "Marking NOK", "Burns", "Crush", "Other",
    "Lack of Materials", "Mismatch", "Pilot Crush", "Drum Thickness",
    "Cracks", "Short Pours", "Stickers", "Damage", "Core Set",
    "Inclusion (sand)", "Heavy Dry Core", "Pinholes"
  ];

  useEffect(() => {
    drawDiagram();
    Streamlit.setFrameHeight(800);
  }, []);

  const drawDiagram = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = 250;
    const centerY = 250;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#e8e8e8';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.beginPath();
    ctx.arc(centerX, centerY, 240, 0, 2 * Math.PI);
    ctx.fillStyle = '#000000';
    ctx.fill();

    for (let i = 0; i < 12; i++) {
      const startAngle = (i * 30 - 90) * Math.PI / 180;
      const endAngle = ((i + 1) * 30 - 90) * Math.PI / 180;
      ctx.beginPath();
      ctx.arc(centerX, centerY, 230, startAngle, endAngle);
      ctx.arc(centerX, centerY, 170, endAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = '#87CEEB';
      ctx.fill();
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.arc(centerX, centerY, 170, 0, 2 * Math.PI);
    ctx.fillStyle = '#9370DB';
    ctx.fill();

    ctx.beginPath();
    ctx.arc(centerX, centerY, 140, 0, 2 * Math.PI);
    ctx.fillStyle = '#808080';
    ctx.fill();

    for (let i = 0; i < 12; i++) {
      const angle = (i * 30 - 90) * Math.PI / 180;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(centerX + 140 * Math.cos(angle), centerY + 140 * Math.sin(angle));
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.arc(centerX, centerY, 35, 0, 2 * Math.PI);
    ctx.fillStyle = '#00CED1';
    ctx.fill();
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(centerX, centerY, 25, 0, 2 * Math.PI);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();

    ctx.fillStyle = '#000000';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 1; i <= 12; i++) {
      const angle = ((i * 30) - 90) * Math.PI / 180;
      const x = centerX + 200 * Math.cos(angle);
      const y = centerY + 200 * Math.sin(angle);
      ctx.fillText(i.toString(), x, y);
    }
  };

  const getClickZone = (x, y) => {
    const centerX = 250;
    const centerY = 250;
    const dx = x - centerX;
    const dy = y - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    let angle = Math.atan2(dy, dx) * 180 / Math.PI + 90;
    if (angle < 0) angle += 360;

    const segment = Math.floor(angle / 30) + 1;

    let ring;
    if (distance <= 25) ring = 'Center';
    else if (distance <= 35) ring = 'CenterRing';
    else if (distance <= 140) ring = 'Inner';
    else if (distance <= 170) ring = 'Middle';
    else if (distance <= 230) ring = 'Outer';
    else if (distance <= 240) ring = 'Border';
    else ring = 'Outside';

    return {
      segment,
      ring,
      distance: Math.round(distance),
      angle: Math.round(angle),
      timestamp: new Date().toISOString()
    };
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    const clickData = getClickZone(x, y);
    setPendingClick(clickData);
    setShowOptionModal(true);

    const ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(255, 0, 0, 0.7)';
    ctx.fill();
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.stroke();
  };

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    setShowOptionModal(false);
    setShowDefectModal(true);
  };

  const handleDefectSelect = (defect) => {
    setSelectedDefect(defect);
    setShowDefectModal(false);
    setShowCavityModal(true);
  };

  const handleSubmit = () => {
    if (!cavity.trim()) {
      alert('Please enter a casting cavity');
      return;
    }

    const finalData = {
      ...pendingClick,
      option: selectedOption,
      defect: selectedDefect,
      cavity: cavity.trim()
    };

    Streamlit.setComponentValue(finalData);

    setLastClick(`Segment ${finalData.segment} | ${finalData.ring} | ${selectedOption} | ${selectedDefect} | Cavity: ${cavity}`);
    setClickCount(prev => prev + 1);

    setShowCavityModal(false);
    setCavity('');
    setPendingClick(null);
    setSelectedOption('');
    setSelectedDefect('');
  };

  return (
    <div className="circle-diagram-container">
      <div className="canvas-wrapper">
        <div className="click-counter">Clicks: {clickCount}</div>
        <canvas
          ref={canvasRef}
          width={500}
          height={500}
          onClick={handleCanvasClick}
          className="circle-canvas"
        />
      </div>

      <div className="info-box">
        {lastClick ? (
          <div className="data-point"><strong>Last Click:</strong> {lastClick}</div>
        ) : (
          <div>Click on the diagram to log a data point</div>
        )}
      </div>

      {showOptionModal && pendingClick && (
        <div className="modal" onClick={() => setShowOptionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Step 1: Select Option</h2>
            <div className="modal-info">
              <p><strong>Segment:</strong> {pendingClick.segment}</p>
              <p><strong>Ring:</strong> {pendingClick.ring}</p>
              <p><strong>Angle:</strong> {pendingClick.angle}°</p>
              <p><strong>Distance:</strong> {pendingClick.distance} px</p>
            </div>
            <p style={{fontWeight: 'bold', marginBottom: '10px'}}>Choose an option:</p>
            <div className="modal-buttons">
              <button className="modal-btn btn-inboard" onClick={() => handleOptionSelect('Inboard')}>Inboard</button>
              <button className="modal-btn btn-outboard" onClick={() => handleOptionSelect('Outboard')}>Outboard</button>
            </div>
          </div>
        </div>
      )}

      {showDefectModal && (
        <div className="modal" onClick={() => {setShowDefectModal(false); setShowOptionModal(true);}}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Step 2: Select Defect Type</h2>
            <div className="selected-option">Selected: {selectedOption}</div>
            <div className="modal-info">
              <p><strong>Segment:</strong> {pendingClick?.segment} | <strong>Ring:</strong> {pendingClick?.ring}</p>
            </div>
            <p style={{fontWeight: 'bold', marginBottom: '5px'}}>Click a defect type:</p>
            <div className="defect-grid">
              {defectTypes.map((defect, idx) => (
                <div key={idx} className="defect-tile" onClick={() => handleDefectSelect(defect)}>{defect}</div>
              ))}
            </div>
          </div>
        </div>
      )}

      {showCavityModal && (
        <div className="modal" onClick={() => {setShowCavityModal(false); setShowDefectModal(true);}}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Step 3: Enter Casting Cavity</h2>
            <div className="selected-option">{selectedOption} | {selectedDefect}</div>
            <div className="modal-info">
              <p><strong>Segment:</strong> {pendingClick?.segment} | <strong>Ring:</strong> {pendingClick?.ring}</p>
            </div>
            <div style={{margin: '20px 0'}}>
              <label style={{display: 'block', marginBottom: '10px', fontWeight: 'bold', color: '#000'}}>Casting Cavity:</label>
              <input
                type="text"
                value={cavity}
                onChange={(e) => setCavity(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
                placeholder="Enter casting cavity..."
                className="cavity-input"
                autoFocus
              />
            </div>
            <button className="modal-btn btn-submit" onClick={handleSubmit}>Submit</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default withStreamlitConnection(CircleDiagram);