/**
 * Product Factory Module - 2
 * Generates complete products (ebooks, courses, tools, etc)
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Package, Play, RefreshCw } from 'lucide-react';

const ProductFactoryModule = () => {
  const [generatingProduct, setGeneratingProduct] = useState(false);
  const [products, setProducts] = useState([
    {
      id: 1,
      name: 'AI Copywriting Masterclass',
      type: 'Course',
      status: 'Published',
      progress: 100,
      files: 12,
      size: '2.4 GB'
    },
    {
      id: 2,
      name: 'Email Template Pack',
      type: 'Templates',
      status: 'Generating',
      progress: 65,
      files: 24,
      size: '450 MB'
    }
  ]);

  const productTypes = [
    { name: 'Ebook', icon: '📚', description: 'AI-written, SEO-optimized ebook' },
    { name: 'Course', icon: '🎓', description: 'Video scripts & course materials' },
    { name: 'Templates', icon: '📋', description: 'Ready-to-use templates' },
    { name: 'Tool', icon: '⚙️', description: 'Micro SaaS tool' },
    { name: 'Prompts', icon: '💬', description: 'AI prompt library' },
    { name: 'Lead Magnet', icon: '🪝', description: 'Free lead generation asset' }
  ];

  const generateProduct = async (type) => {
    setGeneratingProduct(true);
    // Simulate generation
    setTimeout(() => setGeneratingProduct(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-r from-purple-900/50 to-purple-800/50 border-purple-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Package className="w-5 h-5" />
            Product Factory
          </CardTitle>
          <CardDescription className="text-purple-200">
            Generate complete products automatically
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Product Type Selector */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">🏭 Create New Product</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {productTypes.map((type, idx) => (
            <Button
              key={idx}
              onClick={() => generateProduct(type.name)}
              disabled={generatingProduct}
              variant="outline"
              className="h-auto py-4 flex flex-col gap-2 border-slate-700 hover:border-purple-500 hover:bg-purple-900/30"
            >
              <span className="text-2xl">{type.icon}</span>
              <span className="font-semibold text-white">{type.name}</span>
              <span className="text-xs text-slate-400">{type.description}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Generated Products */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">📦 Generated Products</h3>
        <div className="space-y-4">
          {products.map((product) => (
            <Card key={product.id} className="bg-slate-800/50 border-slate-700">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="font-semibold text-white">{product.name}</p>
                    <p className="text-sm text-slate-400">{product.type} • {product.files} files</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-sm font-medium bg-purple-500/30 text-purple-200">
                    {product.status}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="mb-4">
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all"
                      style={{ width: `${product.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-400 mt-1 text-right">{product.progress}%</p>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button className="flex-1 bg-purple-600 hover:bg-purple-700">
                    <Play className="w-4 h-4 mr-2" /> View Product
                  </Button>
                  <Button variant="outline" className="border-slate-600 hover:bg-slate-700/50">
                    <RefreshCw className="w-4 h-4 mr-2" /> Regenerate
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProductFactoryModule;

