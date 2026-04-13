import React, { useState, useEffect, useCallback } from 'react';
import { FolderOpen, Download, Trash2, Plus, Globe, ChevronRight, RefreshCw, BookOpen } from 'lucide-react';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [products, setProducts] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectDetail, setProjectDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [creating, setCreating] = useState(null);
  const [activeTab, setActiveTab] = useState('projects');
  const [selectedPlatform, setSelectedPlatform] = useState(null);
  const [platformGuide, setPlatformGuide] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [projRes, prodRes, platRes] = await Promise.all([
        fetch(`${API}/api/projects`),
        fetch(`${API}/api/products`),
        fetch(`${API}/api/publishing/platforms`),
      ]);
      if (projRes.ok) {
        const d = await projRes.json();
        setProjects(d.projects || []);
      }
      if (prodRes.ok) setProducts(await prodRes.json());
      if (platRes.ok) {
        const d = await platRes.json();
        setPlatforms(d.platforms || []);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openProject = async (projectId) => {
    setSelectedProject(projectId);
    setProjectDetail(null);
    try {
      const r = await fetch(`${API}/api/projects/${projectId}`);
      if (r.ok) {
        const d = await r.json();
        setProjectDetail(d.project || d);
      }
    } catch (_) {}
  };

  const createProject = async (productId) => {
    setCreating(productId);
    try {
      const r = await fetch(`${API}/api/projects/${productId}/create`, { method: 'POST' });
      const d = await r.json();
      if (d.success) {
        await load();
        alert('Project folder created!');
      }
    } catch (e) {
      alert(e.message);
    } finally {
      setCreating(null);
    }
  };

  const downloadProject = async (projectId) => {
    setDownloading(projectId);
    try {
      const r = await fetch(`${API}/api/projects/${projectId}/download`);
      const d = await r.json();
      if (d.success && d.content) {
        const bytes = Uint8Array.from(atob(d.content), (c) => c.charCodeAt(0));
        const blob = new Blob([bytes], { type: 'application/zip' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = d.filename || `${projectId}.zip`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      alert(e.message);
    } finally {
      setDownloading(null);
    }
  };

  const deleteProject = async (projectId) => {
    if (!window.confirm('Delete this project? This cannot be undone.')) return;
    setDeleting(projectId);
    try {
      await fetch(`${API}/api/projects/${projectId}`, { method: 'DELETE' });
      setSelectedProject(null);
      setProjectDetail(null);
      load();
    } catch (e) {
      alert(e.message);
    } finally {
      setDeleting(null);
    }
  };

  const openPlatformGuide = async (platformId) => {
    setSelectedPlatform(platformId);
    setPlatformGuide(null);
    try {
      const r = await fetch(`${API}/api/publishing/guide/${platformId}`);
      if (r.ok) setPlatformGuide(await r.json());
    } catch (_) {}
  };

  const existingProjectIds = new Set(projects.map((p) => p.id || p.product_id));
  const productsWithoutProject = products.filter((p) => !existingProjectIds.has(p.id));

  return (
    <div className="page">
      <div className="page-header">
        <h1><FolderOpen size={28} style={{ marginRight: 8, verticalAlign: 'middle' }} />Projects & Publishing</h1>
        <p>Organize product files, download ZIPs, and get step-by-step publishing guides for every platform</p>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Tab nav */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {['projects', 'publishing'].map((tab) => (
          <button
            key={tab}
            className={`btn ${activeTab === tab ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '6px 18px', fontSize: 13, textTransform: 'capitalize' }}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'projects' ? `📁 Projects (${projects.length})` : '🌐 Publishing Guide'}
          </button>
        ))}
        <button className="btn btn-outline" onClick={load} style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
          <RefreshCw size={14} />Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Loading...</div>
      ) : activeTab === 'projects' ? (
        <div style={{ display: 'grid', gridTemplateColumns: selectedProject ? '1fr 1.4fr' : '1fr', gap: 24 }}>
          {/* Project list */}
          <div>
            {/* Create project from product */}
            {productsWithoutProject.length > 0 && (
              <div className="content-section" style={{ marginBottom: 20 }}>
                <h2>➕ Create Project Folders</h2>
                <p style={{ color: '#888', fontSize: 13, marginBottom: 12 }}>
                  These products don't have project folders yet.
                </p>
                {productsWithoutProject.map((prod) => (
                  <div key={prod.id} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 14px', background: '#1a1a2e', borderRadius: 8, marginBottom: 8,
                    border: '1px solid #333',
                  }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>{prod.title}</div>
                      <div style={{ fontSize: 11, color: '#888' }}>{prod.product_type} • ${prod.price}</div>
                    </div>
                    <button
                      className="btn btn-primary"
                      style={{ fontSize: 12, padding: '5px 12px' }}
                      onClick={() => createProject(prod.id)}
                      disabled={creating === prod.id}
                    >
                      <Plus size={12} style={{ marginRight: 4 }} />
                      {creating === prod.id ? 'Creating...' : 'Create'}
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="content-section">
              <h2>📁 Project Folders ({projects.length})</h2>
              {projects.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#555' }}>
                  <FolderOpen size={40} style={{ marginBottom: 12, opacity: 0.3 }} />
                  <p>No projects yet. Create one from a product above.</p>
                </div>
              ) : projects.map((proj) => (
                <div
                  key={proj.id}
                  onClick={() => openProject(proj.id)}
                  style={{
                    padding: '12px 16px', borderRadius: 8, marginBottom: 8, cursor: 'pointer',
                    background: selectedProject === proj.id ? '#7c3aed20' : '#1a1a2e',
                    border: `1px solid ${selectedProject === proj.id ? '#7c3aed' : '#333'}`,
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{proj.title || proj.id}</div>
                    <div style={{ fontSize: 11, color: '#888', marginTop: 2 }}>
                      {proj.type} • {proj.files?.length || 0} files
                    </div>
                  </div>
                  <ChevronRight size={16} color="#888" />
                </div>
              ))}
            </div>
          </div>

          {/* Project detail panel */}
          {selectedProject && (
            <div className="content-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2>📂 {projectDetail?.title || selectedProject}</h2>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    className="btn btn-primary"
                    style={{ fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}
                    onClick={() => downloadProject(selectedProject)}
                    disabled={downloading === selectedProject}
                  >
                    <Download size={13} />
                    {downloading === selectedProject ? 'Zipping...' : 'Download ZIP'}
                  </button>
                  <button
                    className="btn"
                    style={{ fontSize: 12, background: '#dc354520', color: '#dc3545', border: '1px solid #dc3545' }}
                    onClick={() => deleteProject(selectedProject)}
                    disabled={deleting === selectedProject}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              {projectDetail ? (
                <>
                  {projectDetail.product && (
                    <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 14, marginBottom: 16, fontSize: 13 }}>
                      <div><strong>Type:</strong> {projectDetail.product.product_type}</div>
                      <div><strong>Price:</strong> ${projectDetail.product.price}</div>
                      <div><strong>Status:</strong> {projectDetail.product.status}</div>
                    </div>
                  )}
                  <h3 style={{ fontSize: 14, marginBottom: 10 }}>Files ({projectDetail.files?.length || 0})</h3>
                  {(projectDetail.files || []).map((file, i) => (
                    <div key={i} style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      padding: '8px 12px', background: '#0d0d1a', borderRadius: 6, marginBottom: 4, fontSize: 12,
                    }}>
                      <span style={{ color: '#aaa' }}>📄 {file.path || file.name}</span>
                      <span style={{ color: '#666' }}>{file.size ? `${(file.size / 1024).toFixed(1)}KB` : ''}</span>
                    </div>
                  ))}
                </>
              ) : (
                <p style={{ color: '#666' }}>Loading project details...</p>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Publishing guide tab */
        <div style={{ display: 'grid', gridTemplateColumns: selectedPlatform ? '1fr 1.4fr' : '1fr', gap: 24 }}>
          <div className="content-section">
            <h2><Globe size={18} style={{ marginRight: 6, verticalAlign: 'middle' }} />Publishing Platforms ({platforms.length})</h2>
            {platforms.length === 0 ? (
              <p style={{ color: '#666' }}>No platforms loaded.</p>
            ) : (
              Object.entries(
                platforms.reduce((acc, p) => {
                  const cat = p.category || 'other';
                  if (!acc[cat]) acc[cat] = [];
                  acc[cat].push(p);
                  return acc;
                }, {})
              ).map(([cat, items]) => (
                <div key={cat} style={{ marginBottom: 20 }}>
                  <h3 style={{ textTransform: 'capitalize', fontSize: 13, color: '#888', marginBottom: 8 }}>{cat}</h3>
                  {items.map((plat) => (
                    <div
                      key={plat.id}
                      onClick={() => openPlatformGuide(plat.id)}
                      style={{
                        padding: '10px 14px', borderRadius: 8, marginBottom: 6, cursor: 'pointer',
                        background: selectedPlatform === plat.id ? '#7c3aed20' : '#1a1a2e',
                        border: `1px solid ${selectedPlatform === plat.id ? '#7c3aed' : '#333'}`,
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontSize: 18 }}>{plat.icon || '🌐'}</span>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 13 }}>{plat.name}</div>
                          <div style={{ fontSize: 11, color: '#888' }}>{plat.fees || ''}</div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {plat.automated ? (
                          <span style={{ fontSize: 10, background: '#28a74520', color: '#28a745', padding: '1px 6px', borderRadius: 8 }}>AUTO</span>
                        ) : (
                          <span style={{ fontSize: 10, background: '#ffc10720', color: '#ffc107', padding: '1px 6px', borderRadius: 8 }}>MANUAL</span>
                        )}
                        <ChevronRight size={14} color="#888" />
                      </div>
                    </div>
                  ))}
                </div>
              ))
            )}
          </div>

          {selectedPlatform && (
            <div className="content-section">
              <h2>
                <BookOpen size={18} style={{ marginRight: 6, verticalAlign: 'middle' }} />
                {platformGuide?.name || selectedPlatform} Guide
              </h2>
              {platformGuide ? (
                <>
                  {platformGuide.automated !== undefined && (
                    <div style={{ marginBottom: 16, padding: '10px 14px', borderRadius: 8, background: platformGuide.automated ? '#28a74520' : '#ffc10720' }}>
                      {platformGuide.automated
                        ? '✅ Automated publishing available — we can handle this for you!'
                        : '📝 Manual upload required — follow the steps below'}
                    </div>
                  )}
                  {platformGuide.instructions && (
                    <div style={{ background: '#0d0d1a', borderRadius: 8, padding: 16, marginBottom: 16 }}>
                      <h3 style={{ fontSize: 13, marginBottom: 10 }}>Instructions</h3>
                      <p style={{ fontSize: 13, color: '#ccc', lineHeight: 1.6 }}>{platformGuide.instructions}</p>
                    </div>
                  )}
                  {platformGuide.url && (
                    <a
                      href={platformGuide.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                      style={{ fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 6, textDecoration: 'none' }}
                    >
                      <Globe size={14} />Open {platformGuide.name}
                    </a>
                  )}
                  {platformGuide.product_types?.length > 0 && (
                    <div style={{ marginTop: 16 }}>
                      <h3 style={{ fontSize: 13, marginBottom: 8 }}>Supports</h3>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {platformGuide.product_types.map((t) => (
                          <span key={t} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 10, background: '#7c3aed20', color: '#7c3aed' }}>
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {platformGuide.time_to_publish && (
                    <div style={{ marginTop: 16, fontSize: 13, color: '#aaa' }}>
                      ⏱ Time to publish: <strong style={{ color: '#fff' }}>{platformGuide.time_to_publish}</strong>
                    </div>
                  )}
                </>
              ) : (
                <p style={{ color: '#666' }}>Loading guide...</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProjectsPage;
