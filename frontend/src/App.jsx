import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [documentation, setDocumentation] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('preview');
  const [selectedOption, setSelectedOption] = useState('documentation');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const normalizeGitHubUrl = (url) => {
    try {
      // Remove trailing slash
      url = url.trim().replace(/\/$/, '');
      
      // If URL doesn't start with http/https, add https://
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }
      
      // Remove www. if present
      url = url.replace('www.', '');
      
      // Parse URL to validate and normalize
      const urlObj = new URL(url);
      
      // Ensure it's a GitHub URL
      if (!urlObj.hostname.endsWith('github.com')) {
        throw new Error('Not a GitHub URL');
      }
      
      // Get the path parts
      const pathParts = urlObj.pathname.split('/').filter(Boolean);
      
      // Need at least username/repo
      if (pathParts.length < 2) {
        throw new Error('Invalid repository path');
      }
      
      // Construct final URL with just username/repo
      return `https://github.com/${pathParts[0]}/${pathParts[1]}`;
    } catch (error) {
      console.error(`Error normalizing GitHub URL:`, error);
      return null;
    }
  };

  const handleGenerateDocs = async () => {
    if (!repoUrl) return;
    
    const normalizedUrl = normalizeGitHubUrl(repoUrl);
    if (!normalizedUrl) {
      alert('Please enter a valid GitHub repository URL');
      return;
    }

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
        url: normalizedUrl,
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
    
    // Different formatting based on the selected option
    if (selectedOption === 'documentation') {
      return doc
        .replace(/```markdown\n/g, '')
        .replace(/```\n/g, '')
        .replace(/\\n/g, '\n')
        .replace(/\n\n/g, '\n');
    } else {
      // For Dockerfile and Docker Compose
      return doc
        .replace(/```dockerfile\n/g, '')
        .replace(/```yaml\n/g, '')
        .replace(/```\n/g, '')
        .replace(/\\n/g, '\n')
        .replace(/\n\n/g, '\n');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleGenerateDocs();
    }
  };

  return (
    <div className="min-h-screen bg-[#0D1117] text-white">
      {/* Header */}
      <header className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold">docSmith</h1>
          </div>
          <nav className="flex items-center space-x-6">
            <a 
              href="https://github.com/Jai0401/docSmith" 
              className="flex items-center space-x-2 px-3 py-1.5 bg-[#21262D] rounded-md text-sm text-gray-300 hover:bg-gray-700/50 transition-colors group"
            >
              <svg 
                className="w-5 h-5 text-gray-400 group-hover:text-yellow-400 transition-colors" 
                fill="currentColor" 
                viewBox="0 0 24 24"
              >
                <path d="M12 .25a.75.75 0 01.673.418l3.058 6.197 6.839.994a.75.75 0 01.415 1.279l-4.948 4.823 1.168 6.811a.75.75 0 01-1.088.791L12 18.347l-6.117 3.216a.75.75 0 01-1.088-.79l1.168-6.812-4.948-4.823a.75.75 0 01.416-1.28l6.838-.993L11.328.668A.75.75 0 0112 .25z"/>
              </svg>
              <span>Star Us GitHub</span>
            </a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-4xl font-bold mb-6 text-center bg-gradient-to-r from-blue-400 to-teal-400 bg-clip-text text-transparent">
          Generate documentation from a GitHub repository URL.
          </h2>

          {/* Search Input */}
          <div className="relative mb-8 group">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-teal-500/20 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-200"></div>
            <div className="relative">
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter a GitHub repository URL..."
                className="w-full bg-[#161B22] border border-gray-700/50 rounded-lg px-4 py-3 pr-36 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white placeholder-gray-500 transition-all duration-200"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex space-x-2 items-center">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="px-3 py-1.5 bg-[#21262D] rounded-md text-sm text-gray-300 hover:bg-gray-700/50 transition-colors flex items-center space-x-1 group relative"
                >
                  <span>{selectedOption}</span>
                  <svg 
                    className={`w-4 h-4 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <button
                  onClick={handleGenerateDocs}
                  disabled={loading || !repoUrl}
                  className="px-4 py-1.5 bg-gradient-to-r from-blue-600/80 to-blue-700/80 hover:from-blue-600 hover:to-blue-700 rounded-md text-sm text-white/90 hover:text-white transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:from-blue-600/80 disabled:hover:to-blue-700/80 shadow-lg shadow-blue-500/20"
                >
                  Generate
                </button>
              </div>
            </div>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-24 top-12 w-48 bg-[#161B22] border border-gray-700/50 rounded-lg shadow-xl z-10 backdrop-blur-sm">
                {['documentation', 'dockerfile', 'docker-compose'].map((option) => (
                  <button
                    key={option}
                    onClick={() => {
                      setSelectedOption(option);
                      setIsDropdownOpen(false);
                    }}
                    className={`w-full px-4 py-2.5 text-left text-sm transition-colors first:rounded-t-lg last:rounded-b-lg
                      ${selectedOption === option 
                        ? 'bg-blue-500/10 text-blue-400' 
                        : 'text-gray-300 hover:bg-gray-700/50'}`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${selectedOption === option ? 'bg-blue-400' : 'bg-gray-600'}`}></span>
                      <span>{option}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-2 border-blue-500/20 animate-pulse"></div>
                <div className="absolute top-0 left-0 w-12 h-12 rounded-full border-t-2 border-blue-500 animate-spin"></div>
              </div>
            </div>
          )}

          {/* Results */}
          {documentation && !loading && (
            <div className="bg-[#161B22] rounded-lg border border-gray-700/50 overflow-hidden shadow-xl">
              {/* Results Header */}
              <div className="border-b border-gray-700/50 p-4 flex justify-between items-center bg-gradient-to-r from-gray-800/50 to-transparent">
                <div className="flex space-x-6">
                  <button
                    onClick={() => setView('preview')}
                    className={`text-sm font-medium transition-colors relative ${
                      view === 'preview' ? 'text-blue-400' : 'text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    Preview
                    {view === 'preview' && (
                      <div className="absolute -bottom-4 left-0 right-0 h-0.5 bg-blue-400"></div>
                    )}
                  </button>
                  <button
                    onClick={() => setView('raw')}
                    className={`text-sm font-medium transition-colors relative ${
                      view === 'raw' ? 'text-blue-400' : 'text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    Raw
                    {view === 'raw' && (
                      <div className="absolute -bottom-4 left-0 right-0 h-0.5 bg-blue-400"></div>
                    )}
                  </button>
                </div>
                <button
                  onClick={handleCopy}
                  className="text-sm text-gray-400 hover:text-white transition-colors flex items-center space-x-1 group"
                >
                  <svg 
                    className="w-4 h-4 group-hover:scale-110 transition-transform" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                  </svg>
                  <span>Copy</span>
                </button>
              </div>

              {/* Results Content */}
              <div className="p-6">
                {view === 'raw' ? (
                  <pre className="text-sm text-gray-300 font-mono whitespace-pre-wrap bg-black/20 p-4 rounded-lg">
                    {formatDocumentation(documentation)}
                  </pre>
                ) : (
                  <div className={`${
                    selectedOption === 'documentation' 
                      ? 'prose prose-invert max-w-none' 
                      : 'font-mono text-sm'
                  }`}>
                    {selectedOption === 'documentation' ? (
                      <ReactMarkdown>
                        {formatDocumentation(documentation)}
                      </ReactMarkdown>
                    ) : (
                      <div className="relative group">
                        <div className="absolute -inset-2 bg-gradient-to-r from-blue-500/5 to-teal-500/5 rounded-lg blur-sm"></div>
                        <div className="relative">
                          <div className="flex items-center justify-between mb-2 text-xs text-gray-400">
                            <span>{selectedOption === 'dockerfile' ? 'Dockerfile' : 'docker-compose.yml'}</span>
                            <div className="flex items-center space-x-2">
                              <span className="px-2 py-1 rounded-md bg-blue-500/10 text-blue-400">
                                {selectedOption === 'dockerfile' ? 'Docker' : 'YAML'}
                              </span>
                            </div>
                          </div>
                          <pre className="bg-black/20 p-4 rounded-lg overflow-x-auto">
                            <code className="text-gray-300">
                              {formatDocumentation(documentation)}
                            </code>
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
