export async function api(path,options={}) {
 const token=sessionStorage.getItem('gz_token');
 let response;
 try {response=await fetch('/api'+path,{...options,headers:{...(options.body?{'Content-Type':'application/json'}:{}),...(token?{Authorization:'Bearer '+token}:{}),...options.headers}})}
 catch {throw new Error('Não foi possível conectar à API. Inicie o backend e tente novamente.');}
 const data=await response.json().catch(()=>({}));
 if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:'Verifique os campos e tente novamente.');
 return data;
}
