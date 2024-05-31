import { useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
// import 'codemirror/theme/material.css';
import './App.css';

function App() {
  const [code, setCode] = useState<string>('');
  const [output, setOutput] = useState<string>('');

  const testCode = async () => {
    const response = await fetch('http://127.0.0.1:8000/api/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });
    const result = await response.json();
    setOutput(result.output);
  };

  const submitCode = async () => {
    const response = await fetch(' http://127.0.0.1:8000/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });
    const result = await response.json();
    if (result.success) {
      alert('Code submitted successfully!');
    } else {
      alert('Error submitting code.');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold">Python Code Executor</h1>
      <CodeMirror
        value={code}
        height="200px"
        extensions={[python()]}
        theme="dark"
        onChange={(value) => setCode(value)}
      />
      <div className="mt-4">
        <button onClick={testCode} className="bg-blue-500 text-white px-4 py-2 rounded mr-2">
          Test Code
        </button>
        <button onClick={submitCode} className="bg-green-500 text-white px-4 py-2 rounded">
          Submit
        </button>
      </div>
      <div className="mt-4">
        <h2 className="text-xl font-bold">Output:</h2>
        <pre className="bg-gray-100 p-4 rounded">{output}</pre>
      </div>
    </div>
  );
}

export default App;
