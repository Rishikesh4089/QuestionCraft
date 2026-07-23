// import { useState } from 'react';
// import Sidebar from '../components/Sidebar';
// import SearchPanel from '../components/SearchPanel';
// import GeneratePaper from './GeneratePaper';
// import PaperHistory from './PaperHistory';
// import Settings from './Settings';
// import FAQ from './FAQ';
// import { useAuth } from '../contexts/AuthContext';
// import Home from './Home';

// export default function Dashboard() {
//   const [currentPage, setCurrentPage] = useState('home');
//   const [showSearch, setShowSearch] = useState(false);
//   const { signOut } = useAuth();

//   const handleSignOut = async () => {
//     try {
//       await signOut();
//     } catch (error) {
//       console.error('Error signing out:', error);
//     }
//   };

//   const handleNavigate = (page: string) => {
//     if (page === 'search') {
//       setShowSearch(true);
//     } else {
//       setCurrentPage(page);
//     }
//   };

//   const renderPage = () => {
//     switch (currentPage) {
//       case 'home':
//         return <Home onNavigate={setCurrentPage} />;
//       case 'generate':
//         return <GeneratePaper />;
//       case 'history':
//         return <PaperHistory />;
//       case 'settings':
//         return <Settings />;
//       case 'faq':
//         return <FAQ />;
//       default:
//         return <GeneratePaper />;
//     }
//   };

//   return (
//     <div className="flex h-screen bg-slate-50">
//       <Sidebar currentPage={currentPage} onNavigate={handleNavigate} onSignOut={handleSignOut} />
//       {renderPage()}
//       {showSearch && <SearchPanel onClose={() => setShowSearch(false)} />}
//     </div>
//   );
// }
