import React from 'react';
import { createRoot } from 'react-dom/client';
import AudioDebugger from './AudioDebugger';
import './AudioDebugger.css';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <AudioDebugger />
  </React.StrictMode>
);
