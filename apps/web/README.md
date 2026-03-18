<h1 align="center">Vite React TypeScript Template</h1>
<p align="center">
   <a href="https://vitejs.dev">
      <img alt="Vite" src="https://img.shields.io/badge/Vite-%234646ff?style=for-the-badge&logo=vite&logoColor=white" />
   </a>
   <a href="https://reactjs.org">
      <img alt="React" src="https://img.shields.io/badge/React-%2361DAFB?style=for-the-badge&logo=react&logoColor=white" />
   </a>
   <a href="https://tailwindcss.com">
      <img alt="Tailwind CSS" src="https://img.shields.io/badge/TailwindCSS-%2338B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
   </a>
   <a href="https://www.typescriptlang.org">
      <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-%23007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
   </a>
</p>
<img width="3840" height="2625" alt="template" src="https://github.com/user-attachments/assets/a6081ca1-9bee-41cc-9979-6dde2324c72f" />
<p align="center">
   Template basé sur Vite • React • Tailwind CSS • TypeScript
</p>

## **Structure Du Projet**

```
vite-react-ts-template
├── public/                 — dossier pour fichiers statiques servis tels quels (images, favicons, etc.)
│   └── index.html          — HTML public statique (fichiers accessibles sans build)
├── src/
│   ├── assets/             — images, polices et autres ressources embarquées
│   ├── callApi/            — fonctions / wrappers pour appels API et gestion des requêtes
│   ├── components/         — composants UI réutilisables (boutons, en-têtes, cartes, ...)
│   ├── constants/          — constantes globales (nom de l'application, clés, etc.)
│   │   └── AppName.tsx 
│   ├── hooks/              — hooks React personnalisés (useAuth, useFetch, ...)
│   ├── pages/              — composants de page (routables)
│   │   └── Home.tsx
│   ├── utils/              — fonctions utilitaires pures (formatters, helpers)
│   ├── App.tsx             — composant racine qui compose les routes et le layout
│   ├── main.tsx            — point d'entrée qui monte l'application React dans le DOM
│   └── index.css           — styles globaux (import Tailwind, resets et overrides)
├── index.html              — point d'entrée HTML utilisé par Vite (template de build/dev)
├── package.json            — métadonnées du projet, dépendances et scripts npm
├── tsconfig.json           — configuration TypeScript (options du compilateur)
├── vite.config.ts          — configuration du bundler Vite (plugins, alias, serveur)
├── postcss.config.js       — configuration PostCSS (autoprefixer, plugins CSS)
├── tailwind.config.ts      — configuration Tailwind CSS (thèmes, plugins, purge)
└── README.md               — documentation et instructions d'utilisation du projet
```

## **Packages**

- **Dépendances (runtime):**
  - `react`: ^19.0.0
  - `react-dom`: ^19.0.0
  - `react-router-dom`: ^7.4.0
  - `axios`: ^1.8.4
  - `framer-motion`: ^12.5.0
  - `react-icons`: ^5.5.0
  - `tailwindcss`: ^4.0.15
  - `@tailwindcss/vite`: ^4.0.15
  - `dotenv`: ^16.4.7

- **Dépendances de développement:**
  - `vite`: ^6.2.0
  - `@vitejs/plugin-react`: ^4.3.4
  - `typescript`: ~5.7.2
  - `eslint`: ^9.21.0
  - `@eslint/js`: ^9.21.0
  - `eslint-plugin-react-hooks`: ^5.1.0
  - `eslint-plugin-react-refresh`: ^0.4.19
  - `autoprefixer`: ^10.4.22
  - `globals`: ^15.15.0
  - `@types/react`: ^19.0.10
  - `@types/react-dom`: ^19.0.4
  - `@types/js-cookie`: ^3.0.6
  - `typescript-eslint`: ^8.24.1

> Les versions ci-dessus proviennent du fichier `package.json` du projet. Mettez à jour les versions si vous souhaitez des versions plus récentes.

## **Démarrer Le Projet**

- Prérequis : Node.js (12+ recommandé, préférez la dernière LTS). Assurez-vous que `npm` est disponible.

- Cloner le repo :

```powershell
git clone https://github.com/JulienBNT/VITE-REACT-TYPESCRIPT-TEMPLATE.git
```

- Installer les dépendances :

```powershell
npm install
```

- Lancer le serveur de développement :

```powershell
npm run dev
```

- Construire pour la production :

```powershell
npm run build
```

- Prévisualiser le build de production :

```powershell
npm run preview
```
