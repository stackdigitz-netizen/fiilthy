import React, { useState, useEffect, useCallback } from 'react';
import { FolderOpen, Download, Trash2, Plus, Globe, ChevronRight, RefreshCw, BookOpen, CheckSquare, Square, Clapperboard, Copy, AlertTriangle } from 'lucide-react';
import WorkflowGuide from '../components/WorkflowGuide';
import './Pages.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

/* ─── Score ring ─────────────────────────────────────────────── */
const ScoreRing = ({ score }) => {
  const color = score >= 80 ? '#28a745' : score >= 50 ? '#ffc107' : '#dc3545';
  const r = 28, circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <svg width={72} height={72} style={{ flexShrink: 0 }}>
      <circle cx={36} cy={36} r={r} fill="none" stroke="#333" strokeWidth={6} />
      <circle cx={36} cy={36} r={r} fill="none" stroke={color} strokeWidth={6}
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        transform="rotate(-90 36 36)" />
      <text x={36} y={41} textAnchor="middle" fill={color} fontSize={14} fontWeight={700}>{score}%</text>
    </svg>
  );
};

/* ─── Checklist panel ────────────────────────────────────────── */
const ChecklistPanel = ({ projectId, onScoreChange }) => {
  const [items, setItems] = useState([]);
  const [checked, setChecked] = useState([]);
  const [score, setScore] = useState(0);
  const [ready, setReady] = useState(false);
  const [blocking, setBlocking] = useState([]);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    setLoaded(false);
    fetch(`${API}/api/projects/${projectId}/checklist`)
      .then(r => r.json())
      .then(d => {
        setItems(d.items || []);
        setChecked(d.checked || []);
        setScore(d.score || 0);
        setReady(d.ready || false);
        setBlocking(d.blocking || []);
        setLoaded(true);
        onScoreChange && onScoreChange(d.score || 0, d.ready || false);
      })
      .catch(() => setLoaded(true));
  }, [projectId, onScoreChange]);

  const toggle = async (id) => {
    const next = checked.includes(id) ? checked.filter(x => x !== id) : [...checked, id];
    setChecked(next);
    setSaving(true);
    try {
      const r = await fetch(`${API}/api/projects/${projectId}/checklist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ checked: next }),
      });
      const d = await r.json();
      setScore(d.score || 0);
      setReady(d.ready || false);
      onScoreChange && onScoreChange(d.score || 0, d.ready || false);
      // Refresh blocking list
      fetch(`${API}/api/projects/${projectId}/checklist`)
        .then(r2 => r2.json()).then(d2 => setBlocking(d2.blocking || []));
    } finally {
      setSaving(false);
    }
  };

  if (!loaded) return <div style={{ padding: 24, color: '#666', textAlign: 'center' }}>Loading checklist…</div>;

  // Group by category
  const categories = [...new Set(items.map(i => i.category))];

  return (
    <div>
      {/* Score header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24, padding: '16px 20px', background: '#0d0d1a', borderRadius: 12, border: `1px solid ${ready ? '#28a74540' : '#dc354540'}` }}>
        <ScoreRing score={score} />
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>
            {ready
              ? <span style={{ color: '#28a745' }}>✅ Quality Gate Passed — Ready to publish!</span>
              : <span style={{ color: '#ffc107' }}>⚠️ Not ready — quality gate requires 80%</span>}
          </div>
          <div style={{ fontSize: 12, color: '#888' }}>
            {checked.length} of {items.length} items complete
            {saving && <span style={{ marginLeft: 8, color: '#555' }}>Saving…</span>}
          </div>
          {!ready && blocking.length > 0 && (
            <div style={{ marginTop: 8 }}>
              {blocking.slice(0, 2).map(b => (
                <div key={b} style={{ fontSize: 11, color: '#dc3545', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 2 }}>
                  <AlertTriangle size={10} />blocking: {b}
                </div>
              ))}
              {blocking.length > 2 && <div style={{ fontSize: 11, color: '#888' }}>+{blocking.length - 2} more required items</div>}
            </div>
          )}
        </div>
      </div>

      {/* Checklist by category */}
      {categories.map(cat => (
        <div key={cat} style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#888', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>{cat}</div>
          {items.filter(i => i.category === cat).map(item => {
            const isChecked = checked.includes(item.id);
            return (
              <div
                key={item.id}
                onClick={() => toggle(item.id)}
                style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px',
                  borderRadius: 8, marginBottom: 4, cursor: 'pointer',
                  background: isChecked ? '#28a74510' : '#0d0d1a',
                  border: `1px solid ${isChecked ? '#28a74530' : '#222'}`,
                  transition: 'all 0.15s',
                }}
              >
                {isChecked
                  ? <CheckSquare size={16} color="#28a745" style={{ flexShrink: 0 }} />
                  : <Square size={16} color={item.required ? '#dc3545' : '#555'} style={{ flexShrink: 0 }} />}
                <span style={{ fontSize: 13, color: isChecked ? '#ccc' : '#aaa', flex: 1, textDecoration: isChecked ? 'none' : 'none' }}>
                  {item.label}
                </span>
                {item.required && !isChecked && (
                  <span style={{ fontSize: 10, color: '#dc3545', fontWeight: 600 }}>REQUIRED</span>
                )}
                {item.required && isChecked && (
                  <span style={{ fontSize: 10, color: '#28a745' }}>✓</span>
                )}
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
};

const buildVideoPromptPack = (product = {}) => {
  const title = (product.title || 'Untitled Product').trim();
  const productType = (product.product_type || 'digital product').replaceAll('_', ' ');
  const description = (product.description || product.content || '').trim();
  const shortDescription = description ? description.slice(0, 420) : `A premium ${productType} called ${title}.`;
  const audience = product.target_audience || product.audience || 'buyers looking for a fast, credible transformation';
  const price = product.price ? `priced at $${product.price}` : 'ready for launch';

  return {
    project_title: title,
    product_type: productType,
    generated_at: new Date().toISOString(),
    prompts: [
      {
        id: 'hero-launch',
        title: 'Hero Launch Ad',
        goal: 'Create a cinematic reveal for the project offer',
        platform: 'TikTok / Reels / Shorts',
        duration_seconds: 20,
        aspect_ratio: '9:16',
        prompt: `Create a polished vertical launch ad for ${title}, a ${productType} ${price}. Show bold kinetic typography, premium product mockups, dramatic lighting, fast punch-in camera moves, clean studio background, luxury digital brand feel, persuasive pacing, and a strong final call to action. The audience is ${audience}. Highlight this offer: ${shortDescription}`,
        voiceover: `Meet ${title}. This ${productType} is built for ${audience}. If you want a faster path to results, this is the offer to watch.`,
        cta: `Get ${title} now.`,
      },
      {
        id: 'problem-solution',
        title: 'Problem To Solution',
        goal: 'Frame the project as the answer to a painful problem',
        platform: 'TikTok / Reels / Shorts',
        duration_seconds: 25,
        aspect_ratio: '9:16',
        prompt: `Generate a short-form problem-solution video for ${title}. Open with frustration and chaos, then transition into clarity and momentum once the ${productType} appears. Use split screens, animated captions, mobile-first framing, high-energy motion graphics, before-and-after storytelling, and clear benefit-driven visuals. Base the message on: ${shortDescription}`,
        voiceover: `Still stuck trying to solve this the hard way? ${title} turns the mess into a step-by-step system you can actually use.`,
        cta: 'See how the system works.',
      },
      {
        id: 'demo-walkthrough',
        title: 'Feature Demo Walkthrough',
        goal: 'Show what the project includes and how it feels to use',
        platform: 'Product Demo / Sales Page Video',
        duration_seconds: 35,
        aspect_ratio: '16:9',
        prompt: `Create a clean demo video for ${title}. Show close-up interface or product shots, scrolling pages, zoom-ins on key sections, highlight callouts, minimal premium UI overlays, subtle camera drift, soft editorial lighting, and smooth transitions. Make the viewer feel the value of this ${productType}. Include these details naturally: ${shortDescription}`,
        voiceover: `Inside ${title}, you get a focused ${productType} designed to help ${audience}. Here is what makes it worth having.`,
        cta: 'Watch the full breakdown and download.',
      },
      {
        id: 'ugc-style',
        title: 'UGC Testimonial Style',
        goal: 'Make the project feel socially proven and relatable',
        platform: 'TikTok / Instagram Reels',
        duration_seconds: 18,
        aspect_ratio: '9:16',
        prompt: `Produce a realistic UGC-style promo for ${title}. Use handheld phone framing, authentic creator energy, quick jump cuts, caption overlays, natural room lighting, excited reactions, and direct-to-camera delivery. The creator should explain why this ${productType} stands out for ${audience}. Reference this core offer: ${shortDescription}`,
        voiceover: `I was not expecting ${title} to be this useful. If you want something practical, fast, and actually clear, this is it.`,
        cta: `Try ${title} today.`,
      },
      {
        id: 'launch-countdown',
        title: 'Offer Countdown Push',
        goal: 'Drive urgency for launch or promotion windows',
        platform: 'Ads / Retargeting Video',
        duration_seconds: 15,
        aspect_ratio: '9:16',
        prompt: `Create a punchy countdown-style ad for ${title}. Use large countdown numerals, urgent text animation, product beauty shots, motion blur transitions, energetic soundtrack cues, and a final urgency card. Sell the value of the ${productType} while pushing action. Center the message around: ${shortDescription}`,
        voiceover: `If ${title} is on your list, do not wait. This is your moment to grab the ${productType} and move now.`,
        cta: 'Buy before the offer closes.',
      },
    ],
  };
};

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
  // Quality checklist
  const [projectTab, setProjectTab] = useState('video'); // 'video' | 'files' | 'checklist'
  const [projectScores, setProjectScores] = useState({}); // projectId -> {score, ready}
  const [videoPrompts, setVideoPrompts] = useState(null);
  const [promptsLoading, setPromptsLoading] = useState(false);
  const [copiedPromptId, setCopiedPromptId] = useState(null);

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

  const handleScoreChange = useCallback((projectId) => (score, ready) => {
    setProjectScores(prev => ({ ...prev, [projectId]: { score, ready } }));
  }, []);

  const loadVideoPrompts = useCallback(async (projectId, product) => {
    setPromptsLoading(true);
    setVideoPrompts(null);
    try {
      const r = await fetch(`${API}/api/projects/${projectId}/video-prompts`);
      if (r.ok) {
        const d = await r.json();
        setVideoPrompts(d.video_prompts || null);
      } else if (product) {
        setVideoPrompts(buildVideoPromptPack(product));
      }
    } catch (_) {
      setVideoPrompts(product ? buildVideoPromptPack(product) : null);
    } finally {
      setPromptsLoading(false);
    }
  }, []);

  const openProject = async (projectId) => {
    setSelectedProject(projectId);
    setProjectDetail(null);
    setProjectTab('video');
    setCopiedPromptId(null);
    try {
      const r = await fetch(`${API}/api/projects/${projectId}`);
      if (r.ok) {
        const d = await r.json();
        const detail = d.project || d;
        setProjectDetail(detail);
        loadVideoPrompts(projectId, detail.product || {});
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

  const copyPrompt = async (prompt) => {
    const copyText = [prompt.prompt, '', `Voiceover: ${prompt.voiceover}`, `CTA: ${prompt.cta}`].join('\n');
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(copyText);
        setCopiedPromptId(prompt.id);
        setTimeout(() => setCopiedPromptId(null), 1600);
      }
    } catch (_) {}
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

      <WorkflowGuide page="projects" />

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

                  <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
                    {[
                      { id: 'video', label: 'Video Prompts' },
                      { id: 'checklist', label: 'Quality Gate' },
                      { id: 'files', label: `Files (${projectDetail.files?.length || 0})` },
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        className={`btn ${projectTab === tab.id ? 'btn-primary' : 'btn-outline'}`}
                        style={{ padding: '6px 14px', fontSize: 12 }}
                        onClick={() => setProjectTab(tab.id)}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>

                  {projectTab === 'video' ? (
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                        <Clapperboard size={16} />
                        <h3 style={{ fontSize: 14, margin: 0 }}>Project Video Prompts</h3>
                      </div>
                      <p style={{ fontSize: 12, color: '#888', marginBottom: 16 }}>
                        These prompts are tailored to this project and ready for Sora, Runway, Veo, or any text-to-video workflow.
                      </p>
                      {promptsLoading ? (
                        <p style={{ color: '#666' }}>Generating prompt pack...</p>
                      ) : videoPrompts?.prompts?.length ? (
                        videoPrompts.prompts.map((prompt) => (
                          <div key={prompt.id} style={{ background: '#0d0d1a', border: '1px solid #222', borderRadius: 10, padding: 16, marginBottom: 12 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', marginBottom: 10 }}>
                              <div>
                                <div style={{ fontWeight: 700, fontSize: 14 }}>{prompt.title}</div>
                                <div style={{ fontSize: 11, color: '#888', marginTop: 4 }}>
                                  {prompt.platform} • {prompt.duration_seconds}s • {prompt.aspect_ratio}
                                </div>
                              </div>
                              <button
                                className="btn btn-outline"
                                style={{ padding: '5px 10px', fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}
                                onClick={() => copyPrompt(prompt)}
                              >
                                <Copy size={12} />
                                {copiedPromptId === prompt.id ? 'Copied' : 'Copy'}
                              </button>
                            </div>
                            <div style={{ fontSize: 11, color: '#7c3aed', fontWeight: 600, marginBottom: 6 }}>{prompt.goal}</div>
                            <div style={{ fontSize: 12, color: '#ccc', lineHeight: 1.65, marginBottom: 12 }}>{prompt.prompt}</div>
                            <div style={{ fontSize: 12, color: '#aaa', marginBottom: 8 }}><strong>Voiceover:</strong> {prompt.voiceover}</div>
                            <div style={{ fontSize: 12, color: '#aaa' }}><strong>CTA:</strong> {prompt.cta}</div>
                          </div>
                        ))
                      ) : (
                        <p style={{ color: '#666' }}>No video prompts available for this project yet.</p>
                      )}
                    </div>
                  ) : projectTab === 'checklist' ? (
                    <ChecklistPanel projectId={selectedProject} onScoreChange={handleScoreChange(selectedProject)} />
                  ) : (
                    <>
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
                  )}
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
