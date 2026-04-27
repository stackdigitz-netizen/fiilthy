import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Folder, File, Download, Trash2, Eye, Copy, 
  ChevronRight, ChevronDown, RefreshCw, Plus,
  FileText, Image, Code, Archive
} from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

const FileIcon = ({ filename }) => {
  const ext = filename.split('.').pop()?.toLowerCase();
  const icons = {
    json: <Code size={16} className="text-yellow-400" />,
    md: <FileText size={16} className="text-blue-400" />,
    txt: <FileText size={16} className="text-gray-400" />,
    png: <Image size={16} className="text-green-400" />,
    jpg: <Image size={16} className="text-green-400" />,
    zip: <Archive size={16} className="text-purple-400" />
  };
  return icons[ext] || <File size={16} className="text-gray-400" />;
};

const ProjectFiles = ({ onClose }) => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [loading, setLoading] = useState(false);
  const [fileContent, setFileContent] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
    setLoading(false);
  };

  const selectProject = async (projectId) => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}`);
      if (response.data.success) {
        setSelectedProject(response.data.project);
      }
    } catch (error) {
      console.error('Error loading project:', error);
    }
  };

  const downloadProject = async (projectId) => {
    try {
      setMessage({ type: 'info', text: 'Preparing download...' });
      const response = await axios.get(`${API}/projects/${projectId}/download`);
      
      if (response.data.success) {
        // Create download link
        const link = document.createElement('a');
        link.href = `data:application/zip;base64,${response.data.content}`;
        link.download = response.data.filename;
        link.click();
        setMessage({ type: 'success', text: 'Download started!' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Download failed' });
    }
  };

  const viewFile = async (projectId, filePath) => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}/file?path=${encodeURIComponent(filePath)}`);
      if (response.data.success) {
        setFileContent({
          path: filePath,
          content: response.data.content,
          isBinary: response.data.is_binary
        });
      }
    } catch (error) {
      console.error('Error loading file:', error);
    }
  };

  const copyContent = (content) => {
    navigator.clipboard.writeText(content);
    setMessage({ type: 'success', text: 'Copied to clipboard!' });
    setTimeout(() => setMessage(null), 2000);
  };

  const toggleFolder = (folder) => {
    setExpandedFolders(prev => ({ ...prev, [folder]: !prev[folder] }));
  };

  const groupFilesByFolder = (files) => {
    const grouped = { root: [] };
    files?.forEach(file => {
      const parts = file.path.split('/');
      if (parts.length > 1) {
        const folder = parts[0];
        if (!grouped[folder]) grouped[folder] = [];
        grouped[folder].push({ ...file, name: parts.slice(1).join('/') });
      } else {
        grouped.root.push(file);
      }
    });
    return grouped;
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden border border-white/20 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-teal-600 to-cyan-600 p-6 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Folder size={32} className="text-white" />
              <div>
                <h2 className="text-2xl font-bold text-white">Project Files</h2>
                <p className="text-white/70 text-sm">Organize, download & manage all your products</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={fetchProjects}
                className="bg-white/20 hover:bg-white/30 p-2 rounded-lg transition-all"
              >
                <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
              </button>
              <button
                onClick={onClose}
                className="text-white/70 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mx-6 mt-4 p-3 rounded-lg text-sm ${
            message.type === 'success' ? 'bg-green-500/20 text-green-400' :
            message.type === 'error' ? 'bg-red-500/20 text-red-400' :
            'bg-blue-500/20 text-blue-400'
          }`}>
            {message.text}
          </div>
        )}

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Project List */}
          <div className="w-64 border-r border-white/10 p-4 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">Projects ({projects.length})</h3>
            
            {projects.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Folder size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No projects yet</p>
                <p className="text-xs">Launch a product to create one</p>
              </div>
            ) : (
              <div className="space-y-2">
                {projects.map(project => (
                  <button
                    key={project.id}
                    onClick={() => selectProject(project.id)}
                    className={`w-full text-left p-3 rounded-lg transition-all flex items-center gap-2 ${
                      selectedProject?.id === project.id
                        ? 'bg-teal-500/20 border border-teal-500/50'
                        : 'bg-white/5 hover:bg-white/10 border border-transparent'
                    }`}
                  >
                    <Folder size={18} className="text-teal-400 flex-shrink-0" />
                    <div className="overflow-hidden">
                      <p className="font-medium text-sm truncate">{project.title || project.id}</p>
                      <p className="text-xs text-gray-500">{project.type}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* File Explorer */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {selectedProject ? (
              <>
                {/* Project Header */}
                <div className="p-4 border-b border-white/10 flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{selectedProject.title}</h3>
                    <p className="text-xs text-gray-500">{selectedProject.files?.length || 0} files</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => downloadProject(selectedProject.id)}
                      className="bg-green-500/20 hover:bg-green-500/40 text-green-400 px-4 py-2 rounded-lg flex items-center gap-2 text-sm transition-all"
                    >
                      <Download size={16} />
                      Download ZIP
                    </button>
                  </div>
                </div>

                {/* Files */}
                <div className="flex-1 overflow-y-auto p-4">
                  {(() => {
                    const grouped = groupFilesByFolder(selectedProject.files);
                    return (
                      <div className="space-y-2">
                        {/* Root files */}
                        {grouped.root?.map(file => (
                          <button
                            key={file.path}
                            onClick={() => viewFile(selectedProject.id, file.path)}
                            className="w-full flex items-center gap-3 p-2 hover:bg-white/5 rounded-lg transition-all text-left"
                          >
                            <FileIcon filename={file.name} />
                            <span className="flex-1 text-sm">{file.name}</span>
                            <span className="text-xs text-gray-500">{Math.round(file.size / 1024)}KB</span>
                          </button>
                        ))}
                        
                        {/* Folders */}
                        {Object.entries(grouped).filter(([k]) => k !== 'root').map(([folder, files]) => (
                          <div key={folder}>
                            <button
                              onClick={() => toggleFolder(folder)}
                              className="w-full flex items-center gap-2 p-2 hover:bg-white/5 rounded-lg transition-all"
                            >
                              {expandedFolders[folder] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                              <Folder size={16} className="text-yellow-400" />
                              <span className="font-medium text-sm">{folder}/</span>
                              <span className="text-xs text-gray-500">{files.length} files</span>
                            </button>
                            
                            {expandedFolders[folder] && (
                              <div className="ml-6 border-l border-white/10 pl-4 space-y-1 mt-1">
                                {files.map(file => (
                                  <button
                                    key={file.path}
                                    onClick={() => viewFile(selectedProject.id, `${folder}/${file.name}`)}
                                    className="w-full flex items-center gap-3 p-2 hover:bg-white/5 rounded-lg transition-all text-left"
                                  >
                                    <FileIcon filename={file.name} />
                                    <span className="flex-1 text-sm">{file.name}</span>
                                    <span className="text-xs text-gray-500">{Math.round(file.size / 1024)}KB</span>
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <Folder size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Select a project to view files</p>
                </div>
              </div>
            )}
          </div>

          {/* File Viewer */}
          {fileContent && (
            <div className="w-96 border-l border-white/10 flex flex-col">
              <div className="p-4 border-b border-white/10 flex items-center justify-between">
                <p className="text-sm font-medium truncate">{fileContent.path}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => copyContent(fileContent.content)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-all"
                    title="Copy"
                  >
                    <Copy size={16} />
                  </button>
                  <button
                    onClick={() => setFileContent(null)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-all"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-4">
                {fileContent.isBinary ? (
                  <p className="text-gray-500 text-sm">Binary file - cannot preview</p>
                ) : (
                  <pre className="text-xs font-mono whitespace-pre-wrap text-gray-300">
                    {fileContent.content}
                  </pre>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectFiles;
