import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [documentation, setDocumentation] = useState('');
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('preview');
  const [selectedOption, setSelectedOption] = useState('documentation');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const [hasGenerated, setHasGenerated] = useState(false);

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
      setHasGenerated(true);
    } catch (error) {
      console.error(`Error generating ${selectedOption}:`, error);
      alert(`Failed to generate ${selectedOption}`);
    }
    setLoading(false);
  };

  const handleCopy = () => {
    const contentToCopy = view === 'edit' ? editedContent : formatDocumentation(documentation);
    navigator.clipboard.writeText(contentToCopy).then(() => {
      alert('Content copied!');
    });
  };

  const formatDocumentation = (doc) => {
    if (!doc) return '';
    
    // Different formatting based on the selected option
    if (selectedOption === 'documentation') {
      return doc
        .replace(/```markdown\n/g, '')  // Remove opening markdown marker
        .replace(/```yaml\n/g, '')      // Remove opening yaml marker
        .replace(/```dockerfile\n/g, '') // Remove opening dockerfile marker
        .replace(/```\n/g, '')          // Remove opening marker
        .replace(/```$/gm, '')          // Remove closing marker at end of lines
        .replace(/<end_code>/g, '```')  // Replace <end_code> with triple backticks
        .replace(/\\n/g, '\n')
        .replace(/\n\n/g, '\n');
    } else {
      // For Dockerfile and Docker Compose
      return doc
        .replace(/```dockerfile\n/g, '') // Remove opening dockerfile marker
        .replace(/```yaml\n/g, '')       // Remove opening yaml marker
        .replace(/```\n/g, '')           // Remove opening marker
        .replace(/```$/gm, '')           // Remove closing marker at end of lines
        .replace(/<end_code>/g, '```')   // Replace <end_code> with triple backticks
        .replace(/\\n/g, '\n')
        .replace(/\n\n/g, '\n');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleGenerateDocs();
    }
  };

  useEffect(() => {
    if (documentation) {
      setEditedContent(formatDocumentation(documentation));
    }
  }, [documentation]);

  return (
    <div className="min-h-screen bg-[#0D1117] text-white relative overflow-hidden">
      {/* Background Pattern */}
      <div className="fixed inset-0 z-0">
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-teal-500/5 animate-pulse-slow"></div>
        
        {/* Grid Pattern */}
        <div className="absolute inset-0" 
          style={{
            backgroundImage: `
              linear-gradient(to right, #1F2937 1px, transparent 1px),
              linear-gradient(to bottom, #1F2937 1px, transparent 1px)
            `,
            backgroundSize: '4rem 4rem',
            maskImage: 'radial-gradient(circle at center, black, transparent 80%)',
          }}
        ></div>
        
        {/* Floating Elements */}
        <div className="absolute inset-0">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className={`absolute w-64 h-64 bg-blue-500/5 rounded-full filter blur-3xl animate-float`}
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${i * 2}s`,
                transform: `scale(${1 + Math.random()})`,
              }}
            ></div>
          ))}
        </div>
      </div>

      {/* Content Wrapper - Add relative and z-10 to ensure content stays above background */}
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-gray-800/50 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-3 sm:py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="font-['Inter'] text-lg sm:text-xl font-medium tracking-tight">
                <span className="bg-gradient-to-r from-white to-gray-400/90 bg-clip-text text-transparent">
                  doc
                </span>
                <span className="text-gray-400">
                  Smith
                </span>
              </h1>
            </div>
            <nav className="flex items-center">
              <a 
                href="https://github.com/Jai0401/docSmith" 
                className="group relative overflow-hidden px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-300"
              >
                {/* Background layers */}
                <div className="absolute inset-0 bg-gradient-to-r from-[#1A1D21] to-[#21262D] border border-gray-800"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-teal-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                
                {/* Content */}
                <div className="relative flex items-center space-x-2">
                  <svg 
                    className="w-4 h-4 sm:w-4.5 sm:h-4.5 text-gray-400 group-hover:text-yellow-400 transition-colors duration-300" 
                    viewBox="0 0 16 16"
                    fill="currentColor"
                  >
                    <path d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z" />
                  </svg>
                  <span className="hidden sm:inline text-gray-300 group-hover:text-white transition-colors duration-300">
                    Star on GitHub
                  </span>
                  <span className="sm:hidden text-gray-300 group-hover:text-white transition-colors duration-300">
                    Star
                  </span>
                </div>
              </a>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className={`min-h-[calc(100vh-73px)] transition-all duration-700 ease-in-out ${
          hasGenerated ? 'pt-12' : 'flex items-center'
        }`}>
          <div className={`max-w-7xl w-full mx-auto px-4 transition-all duration-700 ease-in-out ${
            hasGenerated ? 'transform-none' : 'transform -translate-y-16'
          }`}>
            <div className="max-w-3xl mx-auto">
              <h2 className={`font-['Inter'] text-3xl sm:text-5xl tracking-tight leading-[1.15] font-medium mb-6 sm:mb-8 text-center transition-all duration-700 ease-in-out px-4 ${
                hasGenerated ? 'transform-none' : 'transform scale-110'
              }`}>
                <span className="bg-gradient-to-b from-white to-gray-400/80 bg-clip-text text-transparent">
                  Generate documentation from a 
                </span>
                <br className="hidden sm:block" />
                <span className="bg-gradient-to-b from-white to-gray-400/80 bg-clip-text text-transparent">
                  GitHub repository URL.
                </span>
              </h2>

              {/* Search Input */}
              <div className="relative mb-8 group transition-all duration-700 ease-in-out backdrop-blur-sm z-40">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-teal-500/20 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-200"></div>
                <div className="relative">
                  <input
                    type="text"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter a GitHub repository URL..."
                    className="w-full bg-[#161B22] border border-gray-700/50 rounded-lg px-4 py-3 pr-[8.5rem] sm:pr-36 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-white placeholder-gray-500 transition-all duration-200 text-sm sm:text-base"
                  />
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex space-x-2 items-center">
                    <button
                      onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                      className="px-2 sm:px-3 py-1.5 bg-[#1A1D21] border border-gray-800 rounded-md text-xs sm:text-sm text-gray-400 hover:border-gray-700 transition-colors flex items-center space-x-1 group relative"
                    >
                      <span className="hidden sm:inline">{selectedOption}</span>
                      <span className="sm:hidden">{selectedOption.slice(0, 3)}</span>
                      <svg 
                        className={`w-3 h-3 sm:w-4 sm:h-4 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
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
                      className={`px-2 sm:px-4 py-1.5 rounded-md text-xs sm:text-sm transition-all duration-200 ${
                        loading || !repoUrl
                          ? 'bg-[#1A1D21] text-gray-600 border border-gray-800 cursor-not-allowed'
                          : 'bg-[#1E1E1E] text-white border border-gray-700 hover:border-gray-600 hover:bg-[#2A2A2A]'
                      }`}
                    >
                      Generate
                    </button>
                  </div>
                </div>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <div className="absolute right-24 top-12 w-48 bg-[#161B22]/90 backdrop-blur-md border border-gray-700/50 rounded-lg shadow-xl z-50">
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
                <div className="flex flex-col items-center justify-center py-8 sm:py-12 transition-opacity duration-300 px-4 text-center">
                  <div className="relative flex items-center justify-center mb-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-teal-500/20 rounded-full blur-xl"></div>
                    <div className="relative flex items-center space-x-3">
                      <div className="w-3 h-3 rounded-full bg-blue-400/90 animate-loading-dot-1"></div>
                      <div className="w-3 h-3 rounded-full bg-blue-400/90 animate-loading-dot-2"></div>
                      <div className="w-3 h-3 rounded-full bg-blue-400/90 animate-loading-dot-3"></div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-400 font-medium">
                    <span className="inline-flex items-center">
                      <svg 
                        className="w-4 h-4 mr-2 animate-spin" 
                        fill="none" 
                        viewBox="0 0 24 24"
                      >
                        <circle 
                          className="opacity-25" 
                          cx="12" 
                          cy="12" 
                          r="10" 
                          stroke="currentColor" 
                          strokeWidth="4"
                        ></circle>
                        <path 
                          className="opacity-75" 
                          fill="currentColor" 
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Generating {selectedOption}...
                    </span>
                  </div>
                  <div className="mt-2 text-xs text-gray-500">
                    This might take a few seconds
                  </div>
                </div>
              )}

              {/* Results */}
              {documentation && !loading && (
                <div className="bg-[#161B22]/80 backdrop-blur-sm rounded-lg border border-gray-700/50 overflow-hidden shadow-xl transition-all duration-500 ease-in-out animate-fadeIn mx-4 sm:mx-0 z-30">
                  {/* Results Header */}
                  <div className="border-b border-gray-700/50 p-3 sm:p-4 flex justify-between items-center bg-gradient-to-r from-gray-800/50 to-transparent">
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
                        onClick={() => setView('edit')}
                        className={`text-sm font-medium transition-colors relative ${
                          view === 'edit' ? 'text-blue-400' : 'text-gray-400 hover:text-gray-300'
                        }`}
                      >
                        Edit
                        {view === 'edit' && (
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
                  <div className="p-4 sm:p-6">
                    {view === 'edit' ? (
                      <div className="relative group">
                        <div className="absolute -inset-2 bg-gradient-to-r from-blue-500/5 to-teal-500/5 rounded-lg blur-sm"></div>
                        <div className="relative">
                          <div className="flex items-center justify-between mb-2 text-xs text-gray-400">
                            <span>{selectedOption === 'dockerfile' ? 'Dockerfile' : selectedOption === 'docker-compose' ? 'docker-compose.yml' : 'README.md'}</span>
                            <div className="flex items-center space-x-2">
                              <span className="px-2 py-1 rounded-md bg-blue-500/10 text-blue-400">
                                {selectedOption === 'dockerfile' ? 'Docker' : selectedOption === 'docker-compose' ? 'YAML' : 'Markdown'}
                              </span>
                            </div>
                          </div>
                          <textarea
                            value={editedContent}
                            onChange={(e) => setEditedContent(e.target.value)}
                            className="w-full h-[500px] bg-black/20 p-4 rounded-lg text-gray-300 font-mono text-sm resize-none focus:outline-none focus:ring-1 focus:ring-blue-500/50"
                            spellCheck="false"
                          />
                        </div>
                      </div>
                    ) : (
                      <div className={`${
                        selectedOption === 'documentation' 
                          ? 'prose prose-invert max-w-none' 
                          : 'font-mono text-sm'
                      }`}>
                        {selectedOption === 'documentation' ? (
                          <ReactMarkdown>
                            {editedContent}
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
                                  {editedContent}
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
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
