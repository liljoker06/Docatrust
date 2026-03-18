import APP_NAME from '../constants/AppName';
import { FaReact, FaGithub, FaCode } from 'react-icons/fa';
import { SiTypescript, SiVite, SiTailwindcss, SiReactrouter, SiAxios } from 'react-icons/si';
import { MdAnimation } from 'react-icons/md';

export default function Home() {
  const dependencies = [
    { 
      name: "React", 
      version: "19.0.0", 
      description: "Bibliothèque JavaScript pour construire des interfaces utilisateur réactives",
      icon: FaReact,
      color: "text-blue-400"
    },
    { 
      name: "TypeScript", 
      version: "5.7.2", 
      description: "Superset typé de JavaScript pour une meilleure expérience de développement",
      icon: SiTypescript,
      color: "text-blue-600"
    },
    { 
      name: "Vite", 
      version: "6.2.0", 
      description: "Outil de build ultra-rapide et serveur de développement à chaud",
      icon: SiVite,
      color: "text-purple-500"
    },
    { 
      name: "Tailwind CSS", 
      version: "4.0.15", 
      description: "Framework CSS utilitaire pour un styling rapide et consistant",
      icon: SiTailwindcss,
      color: "text-cyan-400"
    },
    { 
      name: "React Router", 
      version: "7.4.0", 
      description: "Solution de routage complète pour les applications React modernes",
      icon: SiReactrouter,
      color: "text-red-500"
    },
    { 
      name: "Framer Motion", 
      version: "12.5.0", 
      description: "Bibliothèque d'animation puissante et intuitive pour React",
      icon: MdAnimation,
      color: "text-indigo-400"
    },
    { 
      name: "Axios", 
      version: "1.8.4", 
      description: "Client HTTP pour effectuer des requêtes API facilement",
      icon: SiAxios,
      color: "text-purple-600"
    },
    { 
      name: "React Icons", 
      version: "5.5.0", 
      description: "Bibliothèque d'icônes populaires intégrées dans React",
      icon: FaCode,
      color: "text-yellow-400"
    },
    { 
      name: "Dotenv", 
      version: "16.4.7", 
      description: "Gestion sécurisée des variables d'environnement",
      icon: FaCode,
      color: "text-green-500"
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-3xl"></div>
        <div className="relative max-w-6xl mx-auto px-4 py-20 text-center">
          <div className="flex justify-center gap-4 mb-6">
            <FaReact className="text-5xl text-blue-400 animate-pulse" />
            <SiVite className="text-5xl text-purple-400 animate-pulse" />
            <SiTailwindcss className="text-5xl text-cyan-400 animate-pulse" />
          </div>
          
          <h1 className="text-6xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 mb-4 drop-shadow-lg">
            {APP_NAME}
          </h1>
          
          <p className="text-xl text-gray-300 mb-8">
            Template 
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-20">
        {/* Description Section */}
        <div className="mb-16 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">Dépendances</h2>
        </div>

        {/* Dependencies Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
          {dependencies.map((dep) => {
            const IconComponent = dep.icon;
            return (
              <div 
                key={dep.name}
                className="group relative bg-gradient-to-br from-gray-800/50 to-gray-900/50 backdrop-blur-xl rounded-2xl p-6 border border-gray-700 hover:border-purple-500 transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/20 transform hover:-translate-y-2"
              >
                {/* Glow Effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-blue-500/0 group-hover:from-purple-500/10 group-hover:to-blue-500/10 rounded-2xl transition-all duration-300"></div>
                
                <div className="relative">
                  {/* Icon */}
                  <div className={`text-5xl mb-4 ${dep.color} group-hover:scale-110 transition-transform duration-300`}>
                    <IconComponent />
                  </div>
                  
                  {/* Content */}
                  <h3 className="text-xl font-bold text-white mb-2">{dep.name}</h3>
                  <p className="text-sm font-mono text-purple-400 mb-3 bg-gray-900/50 px-3 py-1 rounded inline-block">
                    v{dep.version}
                  </p>
                  <p className="text-gray-300 text-sm leading-relaxed">
                    {dep.description}
                  </p>
                </div>

                {/* Border Glow */}
                <div className="absolute inset-0 rounded-2xl border border-transparent group-hover:border-purple-500/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            );
          })}
        </div>

        {/* Getting Started */}
        <div className="bg-gradient-to-r from-purple-900/50 to-blue-900/50 backdrop-blur-xl rounded-2xl p-8 border border-purple-500/30">
          <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
            <FaCode className="text-purple-400" />
            Démarrer
          </h2>
          
          <div className="space-y-4 text-gray-300">
            <div className="bg-gray-900/50 rounded-lg p-4 font-mono text-sm">
              <p className="text-green-400"># Installer les dépendances</p>
              <p className="text-blue-300">npm install</p>
            </div>
            
            <div className="bg-gray-900/50 rounded-lg p-4 font-mono text-sm">
              <p className="text-green-400"># Lancer le serveur de développement</p>
              <p className="text-blue-300">npm run dev</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}