import { useEffect, useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import "./App.css";

interface execution_output_response {
  output: string;
  error: string | undefined;
}
interface code_submit_response {
  success: boolean;
  error: string;
  output: string | undefined;
}
interface code_snippet {
  id: string;
  code: string;
  output: string;
}
function App() {
  const [code, setCode] = useState<string>("");
  const [output, setOutput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [snippets, setSnippets] = useState<code_snippet[]>([]);

  useEffect(() => {
    getSnippet();
  }, []);
  const testCode = async () => {
    setLoading(true);
    const response = await fetch("http://127.0.0.1:8000/api/test", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    }).catch((e) => {
      setOutput(`Error executing the above program: ${e}`);
    });
    if (response) {
      try {
        const result: execution_output_response = await response.json();
        if (result.error) {
          setOutput(result.error);
        } else {
          setOutput(result.output);
        }
      } catch (e) {
        setOutput("Error executing the above program");
      }
    }
    setLoading(false);
  };

  const submitCode = async () => {
    setLoading(true);
    const response = await fetch("http://127.0.0.1:8000/api/submit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ code }),
    });
    const result: code_submit_response = await response.json();
    if (result.success) {
      setSnippets([...snippets, { code, output: result.output || "", id: "" }]);
      alert("Code submitted successfully!");
    } else {
      alert(`Error submitting code.${result.error}`);
    }
    setLoading(false);
  };

  const getSnippet = async () => {
    const response = await fetch("http://127.0.0.1:8000/api/submissions", {
      method: "GET",
    });
    if (!response.ok) {
      alert("error fetching previous code snippets");
      return;
    }
    const result: code_snippet[] = await response.json();
    setSnippets(result);
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
        readOnly={loading}
      />
      <div className="mt-4">
        <button
          onClick={testCode}
          className="bg-blue-500 text-white px-4 py-2 rounded mr-2 disabled:opacity-50"
          disabled={loading}
        >
          Test Code
        </button>
        <button
          onClick={submitCode}
          className="bg-green-500 text-white px-4 py-2 rounded disabled:opacity-50"
          disabled={loading}
        >
          Submit
        </button>
      </div>
      <div className="mt-4">
        <h2 className="text-xl font-bold">Output:</h2>
        <pre className="bg-gray-100 p-4 rounded">{output}</pre>
      </div>
      <h1 className="text-2xl font-bold mb-4">Code Snippets</h1>
      <div className="grid grid-cols-1 gap-4">
        {snippets.map((snippet) => (
          <div
            key={snippet.id}
            className="p-4 border rounded-lg shadow-md bg-white cursor-pointer"
            onClick={() => {
              setOutput(snippet.output);
              setCode(snippet.code);
            }}
          >
            <div className="mb-2">
              <h2 className="font-semibold">Code:</h2>
              <pre className="bg-gray-100 p-2 rounded">{snippet.code}</pre>
            </div>
            <div>
              <h2 className="font-semibold">Output:</h2>
              <pre className="bg-gray-100 p-2 rounded">{snippet.output}</pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
