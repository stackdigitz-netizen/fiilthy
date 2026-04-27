/**
 * ProductFilesService - Reads and parses product files
 * Converts raw files into structured product data
 */

import API_URL from '../config/api';

const API_BASE_URL = API_URL;

const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
};

export class ProductFilesService {
  static async readErrorMessage(response, fallbackMessage) {
    try {
      const data = await response.json();
      if (typeof data?.detail === 'string' && data.detail.trim()) {
        return data.detail;
      }
      if (typeof data?.message === 'string' && data.message.trim()) {
        return data.message;
      }
    } catch {
      // Ignore parse failures and fall through.
    }

    try {
      const text = await response.text();
      if (text.trim()) {
        return text;
      }
    } catch {
      // Ignore text parse failures and use the fallback.
    }

    return fallbackMessage;
  }

  /**
   * Scans for all products in the system
   */
  static async getAllProducts() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/products`);
      if (!response.ok) throw new Error('Failed to fetch products');
      return await response.json();
    } catch (error) {
      console.error('Error fetching products:', error);
      return [];
    }
  }

  /**
   * Read a single product's files and parse them
   */
  static async getProductDetails(productId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
      if (!response.ok) throw new Error('Failed to fetch product details');
      
      const data = await response.json();
      return this.parseProductData(data);
    } catch (error) {
      console.error('Error fetching product details:', error);
      return null;
    }
  }

  /**
   * Parse product JSON and related files
   */
  static parseProductData(rawData) {
    return {
      id: rawData.id || rawData._id,
      title: rawData.title || rawData.name,
      description: rawData.description,
      type: rawData.type || 'digital',
      fileCount: rawData.fileCount || 0,
      files: rawData.files || [],
      videoPrompts: rawData.videoPrompts || [],
      marketingContent: rawData.marketingContent || {},
      thumbnail: rawData.thumbnail || rawData.image,
      price: rawData.price,
      createdAt: rawData.createdAt,
      tags: rawData.tags || [],
    };
  }

  /**
   * Generate marketing content from product
   */
  static async generateMarketingContent(productId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/products/${productId}/generate-marketing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) throw new Error('Failed to generate marketing content');
      return await response.json();
    } catch (error) {
      console.error('Error generating marketing:', error);
      return null;
    }
  }

  /**
   * Generate email campaign from product
   */
  static async generateEmailCampaign(productId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/products/${productId}/generate-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      
      if (!response.ok) throw new Error('Failed to generate email');
      return await response.json();
    } catch (error) {
      console.error('Error generating email:', error);
      return null;
    }
  }

  /**
   * Download a product bundle directly for the authenticated app owner/operator.
   */
  static async downloadOwnerBundle(product) {
    const response = await fetch(`${API_BASE_URL}/api/fiilthy/owner-download/${product.id}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(await this.readErrorMessage(response, 'Failed to download product bundle'));
    }

    const blob = await response.blob();
    const contentDisposition = response.headers.get('content-disposition') || '';
    const filenameMatch = contentDisposition.match(/filename="?([^\"]+)"?/i);
    const fallbackFilename = `${(product.title || 'product').replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '_') || 'product'}.zip`;
    const filename = filenameMatch?.[1] || fallbackFilename;

    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(objectUrl);
  }

  /**
   * Extract marketing hooks from video prompts
   */
  static extractMarketingAssets(product) {
    const assets = {
      videoScripts: [],
      hooks: [],
      voiceovers: [],
      ctas: [],
      captions: [],
    };

    if (product.videoPrompts && Array.isArray(product.videoPrompts)) {
      product.videoPrompts.forEach((prompt) => {
        if (prompt.script) assets.videoScripts.push(prompt.script);
        if (prompt.hook) assets.hooks.push(prompt.hook);
        if (prompt.voiceover) assets.voiceovers.push(prompt.voiceover);
        if (prompt.cta) assets.ctas.push(prompt.cta);
        if (prompt.caption) assets.captions.push(prompt.caption);
      });
    }

    return assets;
  }
}
