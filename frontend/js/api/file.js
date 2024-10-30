import { request } from '../utils/request.js';

export const fileApi = {
    // 上传文件
    upload: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return request('/api/v1/files/upload', {
            method: 'POST',
            body: formData,
            // 不设置Content-Type，让浏览器自动处理
            headers: {}
        });
    },

    // 获取文件列表
    getList: () => {
        return request('/api/v1/files');
    },

    // 删除文件
    delete: (fileId) => {
        return request(`/api/v1/files/${fileId}`, {
            method: 'DELETE'
        });
    }
}; 