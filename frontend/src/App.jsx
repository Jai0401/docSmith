import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [documentation, setDocumentation] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('preview'); // 'raw' or 'preview'

  const handleGenerateDocs = async () => {
    setLoading(true);
    try {
      const response = await axios.post('https://docsmith.onrender.com/generate-docs-from-url', { url: repoUrl });
      setDocumentation(response.data);
    } catch (error) {
      console.error('Error generating documentation:', error);
      alert('Failed to generate documentation');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(documentation).then(() => {
      alert('Documentation copied!');
    });
  };

  const formatDocumentation = (doc) => {
    return doc.replace(/\\n/g, '\n').replace(/\n\n/g, '\n');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-6">
      <header className="text-center mb-8">
        <h1 className="text-4xl font-semibold text-black">docSmith</h1>
        <p className="text-lg text-gray-600">Generate documentation from a GitHub repository URL.</p>
      </header>
      <div className="w-full max-w-3xl bg-white p-6 rounded-lg shadow-lg">
        <div className="mb-4">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="Enter GitHub repository URL"
            className="w-full p-4 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div className="flex justify-between mb-4">
          <button
            onClick={handleGenerateDocs}
            disabled={loading}
            className="bg-black text-white py-2 px-6 rounded-lg shadow-md hover:bg-gray-800 focus:outline-none disabled:opacity-50"
          >
            Generate
          </button>
        </div>

        {loading && (
          <div className="flex justify-center items-center">
            <div className="animate-spin border-t-4 border-blue-600 border-solid rounded-full w-12 h-12"></div>
            <p className="ml-4 text-lg text-gray-600">Processing...</p>
          </div>
        )}

        {documentation && (
          <div className="mt-6">
            <div className="flex justify-between mb-4">
              <div>
                <button
                  onClick={() => setView('raw')}
                  className="bg-gray-200 text-gray-800 py-2 px-6 rounded-lg hover:bg-gray-300"
                >
                  Raw
                </button>
                <button
                  onClick={() => setView('preview')}
                  className="bg-gray-200 text-gray-800 py-2 px-6 rounded-lg hover:bg-gray-300 ml-2"
                >
                  Preview
                </button>
              </div>
              <button
                onClick={handleCopy}
                className="bg-green-600 text-white py-2 px-6 rounded-lg shadow-md hover:bg-green-700"
              >
                Copy
              </button>
            </div>

            {view === 'raw' ? (
              <pre className="bg-gray-100 p-4 rounded-lg text-sm text-gray-800 font-mono overflow-x-auto">{formatDocumentation(documentation)}</pre>
            ) : (
              <div className="bg-gray-100 p-4 rounded-lg text-sm text-gray-800">
                <ReactMarkdown
                  className="prose text-gray-800"
                  components={{
                    h1: ({ node, ...props }) => <h1 {...props} className="text-3xl font-semibold text-blue-600" />,
                    h2: ({ node, ...props }) => <h2 {...props} className="text-2xl font-semibold text-blue-500" />,
                    h3: ({ node, ...props }) => <h3 {...props} className="text-xl font-semibold text-blue-400" />,
                  }}
                >
                  {formatDocumentation(documentation)}
                </ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
