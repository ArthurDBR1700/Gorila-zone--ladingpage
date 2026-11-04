import {defineConfig} from 'vite';
export default defineConfig({server:{port:5173,strictPort:true,allowedHosts:['terminal.local'],proxy:{'/api':'http://127.0.0.1:8000'}}});
