import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [documentation, setDocumentation] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('preview'); // 'raw' or 'preview'
  const [selectedOption, setSelectedOption] = useState('documentation');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleGenerateDocs = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      switch (selectedOption) {
        case 'documentation':
          endpoint = 'generate-docs-from-url';
          break;
        case 'dockerfile':
          endpoint = 'generate-dockerfile';
          break;
        case 'docker-compose':
          endpoint = 'generate-docker-compose';
          break;
        default:
          endpoint = 'generate-docs-from-url';
      }

      const response = await axios.post(`https://docsmith.onrender.com/${endpoint}`, { 
        url: repoUrl,
        type: selectedOption 
      });
      
      setDocumentation(response.data);
    } catch (error) {
      console.error(`Error generating ${selectedOption}:`, error);
      alert(`Failed to generate ${selectedOption}`);
    }
    setLoading(false);
  };

  const handleCopy = () => {
    const formattedContent = formatDocumentation(documentation);
    navigator.clipboard.writeText(formattedContent).then(() => {
      alert('Content copied!');
    });
  };

  const formatDocumentation = (doc) => {
    if (!doc) return '';
    return doc
      .replace(/```markdown\n/g, '')  // Remove opening markdown tags
      .replace(/```\n/g, '')          // Remove closing tags
      .replace(/\\n/g, '\n')          // Handle newlines
      .replace(/\n\n/g, '\n');        // Remove double newlines
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4 sm:p-6">
      <header className="text-center mb-6 sm:mb-8">
        <h1 className="text-3xl sm:text-4xl font-semibold text-black">docSmith</h1>
        <p className="text-base sm:text-lg text-gray-600">Generate documentation from a GitHub repository URL.</p>
      </header>
      <div className="w-full max-w-3xl bg-white p-4 sm:p-6 rounded-lg shadow-lg">
        <div className="mb-4">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder={`Enter GitHub repository URL for ${selectedOption}`}
            className="w-full p-4 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 mb-4">
          <button
            onClick={handleGenerateDocs}
            disabled={loading}
            className="w-full sm:w-auto bg-black text-white py-2 px-6 rounded-lg shadow-md hover:bg-gray-800 focus:outline-none disabled:opacity-50"
          >
            Generate
          </button>
          <div className="relative w-full sm:w-auto">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="w-full sm:w-auto bg-white border border-gray-300 px-4 py-2 rounded-lg inline-flex items-center justify-between"
            >
              <span className="mr-2">{selectedOption.charAt(0).toUpperCase() + selectedOption.slice(1)}</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {isDropdownOpen && (
              <div className="absolute left-0 right-0 sm:w-48 mt-1 rounded-lg bg-white shadow-lg z-10 border border-gray-200">
                <div className="py-1">
                  {['documentation', 'dockerfile', 'docker-compose'].map((option) => (
                    <button
                      key={option}
                      onClick={() => {
                        setSelectedOption(option);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-2 hover:bg-gray-100 ${
                        selectedOption === option ? 'bg-blue-50 text-blue-600' : 'text-gray-800'
                      }`}
                    >
                      {option.charAt(0).toUpperCase() + option.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {loading && (
          <div className="flex justify-center items-center">
            <div className="animate-spin border-t-4 border-blue-600 border-solid rounded-full w-12 h-12"></div>
            <p className="ml-4 text-lg text-gray-600">Processing...</p>
          </div>
        )}

        {documentation && (
          <div className="mt-6">
            <div className="flex flex-col sm:flex-row justify-between gap-4 mb-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setView('raw')}
                  className="flex-1 sm:flex-none bg-gray-200 text-gray-800 py-2 px-6 rounded-lg hover:bg-gray-300"
                >
                  Raw
                </button>
                <button
                  onClick={() => setView('preview')}
                  className="flex-1 sm:flex-none bg-gray-200 text-gray-800 py-2 px-6 rounded-lg hover:bg-gray-300"
                >
                  Preview
                </button>
              </div>
              <button
                onClick={handleCopy}
                className="w-full sm:w-auto bg-green-600 text-white py-2 px-6 rounded-lg shadow-md hover:bg-green-700"
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
