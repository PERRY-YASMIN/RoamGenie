import { Link, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PlanPage from "./pages/PlanPage";
function Placeholder({title}) { return <main className="panel"><p className="eyebrow">Milestone starter</p><h1>{title}</h1><p>This screen is assigned in Mercy's handbook and is not implemented yet.</p></main>; }
export default function App() { return <div className="app-shell"><header><Link className="brand" to="/">RoamGenie</Link><nav aria-label="Main navigation"><Link to="/plan">Plan a trip</Link><Link to="/destinations">Destinations</Link><Link to="/login">Log in</Link></nav></header><Routes><Route path="/" element={<HomePage/>}/><Route path="/plan" element={<PlanPage/>}/><Route path="/destinations" element={<Placeholder title="Destinations"/>}/><Route path="/login" element={<Placeholder title="Log in"/>}/><Route path="*" element={<Placeholder title="Page not found"/>}/></Routes><footer>DBMS course implementation starter · Mock AI by default</footer></div>; }

