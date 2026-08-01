const API_BASE=import.meta.env.VITE_API_BASE_URL??"http://127.0.0.1:8000/api/v1";
export async function previewPlan(payload){const response=await fetch(`${API_BASE}/plans/preview`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});if(!response.ok){const body=await response.json().catch(()=>null);throw new Error(body?.error?.message??body?.detail?.[0]?.msg??"Could not create the preview.");}return response.json();}

