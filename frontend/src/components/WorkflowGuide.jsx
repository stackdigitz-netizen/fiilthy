import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Lightbulb, CheckCircle, ArrowRight, AlertCircle } from 'lucide-react';

/**
 * Interactive Workflow Guide Component
 * Shows context-aware next steps and guidance for maximum productivity
 */
const WorkflowGuide = ({ 
  page = 'products',
  hasProducts = false,
  hasGeneratedPosts = false,
  completedSteps = []
}) => {
  const [collapsed, setCollapsed] = useState(false);

  // Define workflows for each page
  const workflows = {
    products: {
      title: '🚀 Product Creation Workflow',
      color: '#7c3aed',
      steps: [
        {
          id: 'describe-product',
          label: 'Describe Your Product Idea',
          description: 'Write a concept like "AI email course" and let AI generate everything',
          action: 'Generate Product',
          completed: hasProducts,
          tips: ['Be specific', 'Include target audience', 'Mention the transformation']
        },
        {
          id: 'generate-product',
          label: 'Generate with AI',
          description: 'Click "⚡ Generate Product" — AI creates title, description, image, marketing copy',
          completed: hasProducts,
          tips: ['Takes 30-60 seconds', 'Results are immediately usable', 'Save or regenerate']
        },
        {
          id: 'review-content',
          label: 'Review Generated Content',
          description: 'Check product details, price range, target audience, keywords',
          completed: hasProducts,
          tips: ['Tweak keywords if needed', 'Adjust price', 'Keep description snappy']
        },
        {
          id: 'next-social',
          label: '→ Create Social Posts',
          description: 'Click "Create Posts" button to go to Social Media page',
          action: 'Go to Social Media',
          completed: hasGeneratedPosts,
          next: true,
          tips: ['Each product gets multi-platform content', 'Posts are pre-optimized', '3-5 posts per platform']
        }
      ]
    },
    'social-media': {
      title: '📱 Social Media Campaign Workflow',
      color: '#0ea5e9',
      steps: [
        {
          id: 'select-product',
          label: '1. Select a Product',
          description: 'Choose the product you want to create posts for',
          completed: !hasGeneratedPosts,
          tips: ['Use the dropdown', 'Or click "Create Posts" from Products page to auto-select']
        },
        {
          id: 'select-platforms',
          label: '2. Choose Platforms',
          description: 'Select which social networks you want content for (TikTok, Instagram, X, LinkedIn, YouTube)',
          completed: false,
          tips: ['TikTok: highest engagement', 'LinkedIn: B2B audience', 'YouTube: long-form content']
        },
        {
          id: 'generate-posts',
          label: '3. Generate Posts',
          description: 'Click "Generate Multi-Platform Posts" — AI creates 3-5 posts per platform optimized for each',
          completed: hasGeneratedPosts,
          tips: ['Each post is platform-specific', 'Includes captions, hashtags, timing', 'Takes 1-2 minutes']
        },
        {
          id: 'review-posts',
          label: '4. Review & Edit',
          description: 'Look at generated posts. Copy text to clipboard or delete posts you don\'t want',
          completed: hasGeneratedPosts,
          tips: ['Edit directly in the preview', 'Copy posts to your clipboard', 'Delete unwanted variations']
        },
        {
          id: 'open-platform',
          label: '5. Post to Platform',
          description: 'Click the colored "Open [Platform] →" button. This opens that platform\'s post screen with your text pre-filled',
          completed: false,
          next: true,
          tips: ['Twitter/X: Pre-filled with your caption', 'LinkedIn: Same pre-fill', 'TikTok: Opens upload screen', 'Add images/video there']
        },
        {
          id: 'schedule-posts',
          label: '6. Schedule All Posts (Optional)',
          description: 'Click "Schedule All Posts" to auto-post at optimal times',
          completed: false,
          tips: ['Times are platform-optimized', 'Spreads posts over 24-48 hours', 'Maximizes reach']
        }
      ]
    },
    projects: {
      title: '📁 Project & Publishing Workflow',
      color: '#16a34a',
      steps: [
        {
          id: 'select-product',
          label: 'Select a Product',
          description: 'Filter or find the product you want to create a project/sales files for',
          completed: false,
          tips: ['Projects organize all files', 'One project per product', 'Download as ZIP for sharing']
        },
        {
          id: 'create-project',
          label: 'Create Project Folder',
          description: 'Click "Create Project" — organizes video prompts, landing pages, sales pages',
          completed: false,
          tips: ['Auto-generates 5 video prompt packs', 'Creates sales page templates', 'Bundles all assets']
        },
        {
          id: 'video-prompts',
          label: 'Get Video Prompts',
          description: 'View 5 pre-written video scripts for TikTok, Reels, Shorts (hero, problem-solution, demo, UGC, countdown)',
          completed: false,
          tips: ['Copy prompts to use with video AIs', 'Each has voiceover + CTA', 'Platform-optimized']
        },
        {
          id: 'download-files',
          label: 'Download Project Files',
          description: 'Click "Download ZIP" to get all files locally — landing page, sales page, video scripts, checklist',
          completed: false,
          tips: ['ZIP includes everything', 'HTML templates ready to customize', 'Hosted files included']
        },
        {
          id: 'publishing-guide',
          label: 'Follow Publishing Guide',
          description: 'Go to "Publishing Guide" tab — step-by-step for each platform (Gumroad, Etsy, Shopify, etc)',
          completed: false,
          next: true,
          tips: ['Gumroad: 5 min setup', 'Etsy: Upload + pricing', 'Shopify: Full store setup']
        }
      ]
    },
    hunter: {
      title: '🎯 Opportunity Hunter Workflow',
      color: '#f59e0b',
      steps: [
        {
          id: 'set-preferences',
          label: 'Set Search Preferences',
          description: 'Enter keywords, demand score threshold, and niche category',
          completed: false,
          tips: ['Broader keywords = more results', 'Higher demand = more competitive', 'Pick 3-5 keywords']
        },
        {
          id: 'scan-opportunities',
          label: 'Scan for Opportunities',
          description: 'Click "Scan Opportunities" — AI finds trending gaps in markets',
          completed: false,
          tips: ['Scans 1000s of markets', 'Ranks by demand vs competition', 'Takes 1-2 minutes']
        },
        {
          id: 'review-results',
          label: 'Review Opportunities',
          description: 'See trending opportunities ranked by profit potential and validation',
          completed: false,
          tips: ['Green = High opportunity', 'Yellow = Medium', 'Red = Saturated']
        },
        {
          id: 'create-team',
          label: 'Create Agent Team',
          description: 'For top opportunities, click "Create Agent Team" — assigns specialized AI agents to execute',
          completed: false,
          tips: ['Analyst agent', 'Designer agent', 'Copywriter agent', 'Content creator agent']
        },
        {
          id: 'auto-execute',
          label: 'Monitor Execution',
          description: 'Agents automatically research, design, write, and create content for that opportunity',
          completed: false,
          next: true,
          tips: ['Real-time progress tracking', 'Can take 1-4 hours', 'Results auto-added to Products']
        }
      ]
    },
    factory: {
      title: '⚙️ Product Factory Workflow',
      color: '#ec4899',
      steps: [
        {
          id: 'review-automation',
          label: 'Check Automation Tab',
          description: 'See which integrations are connected (Gumroad, Stripe, TikTok, Instagram, OpenAI, etc)',
          completed: false,
          tips: ['Green = Connected', 'Red = Not setup', 'Settings page to add credentials']
        },
        {
          id: 'start-cycle',
          label: 'Start Factory Cycle',
          description: 'Click "Start Cycle" button to kickoff autonomous product creation',
          completed: false,
          tips: ['Runs in background', 'Watch progress bar advance', '45 min average per cycle']
        },
        {
          id: 'stages',
          label: 'Monitor 8 Stages',
          description: 'Factory auto-progresses: Analyze trends → Select niche → Generate content → Brand assets → Sales funnel → Social content → Publish prep → Finalization',
          completed: false,
          tips: ['Each stage is fully automated', 'No manual steps needed', 'Results saved to Products']
        },
        {
          id: 'review-output',
          label: 'Review Generated Products',
          description: 'When cycle completes (100%), check the Products page for new items',
          completed: false,
          tips: ['Product details pre-filled', 'Branding assets included', 'Ready to post/sell immediately']
        },
        {
          id: 'publish-sell',
          label: 'Publish & Sell',
          description: 'From Products page, click "Create Posts" or "Sell via Stripe" to monetize',
          completed: false,
          next: true,
          tips: ['Multi-channel publishing', 'Automatic social posting', 'Stripe/Gumroad/Etsy integration']
        }
      ]
    }
  };

  const workflow = workflows[page] || workflows.products;
  const currentStep = workflow.steps.find(s => !s.completed) || workflow.steps[workflow.steps.length - 1];
  const progress = ((workflow.steps.filter(s => s.completed).length / workflow.steps.length) * 100).toFixed(0);

  return (
    <div style={{
      backgroundColor: '#fff',
      border: `2px solid ${workflow.color}40`,
      borderRadius: '12px',
      overflow: 'hidden',
      marginBottom: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
    }}>
      {/* Header */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        style={{
          width: '100%',
          padding: '16px',
          backgroundColor: `${workflow.color}10`,
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, textAlign: 'left' }}>
          <Lightbulb size={20} color={workflow.color} />
          <div>
            <div style={{ fontWeight: 700, fontSize: '15px', color: '#000' }}>{workflow.title}</div>
            <div style={{ fontSize: '12px', color: '#666' }}>Step {workflow.steps.filter(s => s.completed).length + 1} of {workflow.steps.length}</div>
          </div>
          <div style={{
            height: '6px', width: '80px', backgroundColor: '#e0e0e0', borderRadius: '3px', marginLeft: 'auto'
          }}>
            <div style={{
              height: '100%', width: `${progress}%`, backgroundColor: workflow.color,
              borderRadius: '3px', transition: 'width 0.3s'
            }} />
          </div>
        </div>
        {collapsed ? <ChevronDown size={18} /> : <ChevronUp size={18} />}
      </button>

      {/* Content */}
      {!collapsed && (
        <div style={{ padding: '16px', borderTop: `1px solid ${workflow.color}20` }}>
          {/* Current step highlight */}
          {currentStep && !currentStep.completed && (
            <div style={{
              padding: '12px',
              backgroundColor: `${workflow.color}15`,
              borderLeft: `4px solid ${workflow.color}`,
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{
                  width: '24px', height: '24px', borderRadius: '50%',
                  backgroundColor: workflow.color, color: '#fff',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '12px', fontWeight: 700, flexShrink: 0
                }}>
                  ⚡
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: '13px', marginBottom: '4px' }}>
                    🎯 Next Step: {currentStep.label}
                  </div>
                  <div style={{ fontSize: '13px', color: '#555', lineHeight: '1.5', marginBottom: '8px' }}>
                    {currentStep.description}
                  </div>
                  {currentStep.tips && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {currentStep.tips.map((tip, i) => (
                        <span key={i} style={{
                          fontSize: '11px', padding: '2px 8px', backgroundColor: '#fff',
                          border: `1px solid ${workflow.color}30`, borderRadius: '12px', color: '#666'
                        }}>
                          💡 {tip}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* All steps */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {workflow.steps.map((step, idx) => (
              <div key={step.id} style={{
                display: 'flex', alignItems: 'flex-start', gap: '12px',
                opacity: step.completed ? 0.6 : 1,
                padding: '10px', borderRadius: '8px',
                backgroundColor: step.completed ? '#f5f5f5' : 'transparent'
              }}>
                <div style={{ marginTop: '3px' }}>
                  {step.completed ? (
                    <CheckCircle size={18} color="#22c55e" />
                  ) : (
                    <div style={{
                      width: '18px', height: '18px', borderRadius: '50%',
                      border: `2px solid ${workflow.color}`,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '10px', fontWeight: 700, color: workflow.color
                    }}>
                      {idx + 1}
                    </div>
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontWeight: 600, fontSize: '13px', color: '#000',
                    textDecoration: step.completed ? 'line-through' : 'none'
                  }}>
                    {step.label}
                  </div>
                  {!step.completed && (
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                      {step.description}
                    </div>
                  )}
                </div>
                {step.next && !step.completed && (
                  <ArrowRight size={16} color={workflow.color} style={{ marginTop: '2px', flexShrink: 0 }} />
                )}
              </div>
            ))}
          </div>

          {/* Completion message */}
          {workflow.steps.every(s => s.completed) && (
            <div style={{
              padding: '12px',
              backgroundColor: '#dcfce7',
              border: '1px solid #86efac',
              borderRadius: '6px',
              marginTop: '12px',
              fontSize: '13px', color: '#166534', fontWeight: 600,
              display: 'flex', alignItems: 'center', gap: '8px'
            }}>
              <CheckCircle size={16} /> Workflow complete! Ready for the next stage.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowGuide;
