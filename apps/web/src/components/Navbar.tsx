import React from 'react';
import { Link } from 'react-router-dom';
import { FaBars, FaTimes } from 'react-icons/fa';
import { useState } from 'react';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              Docatrust
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className="text-gray-700 hover:text-blue-600 font-medium transition duration-300"
            >
              Accueil
            </Link>
            <Link
              to="/login"
              className="text-gray-700 hover:text-blue-600 font-medium transition duration-300"
            >
              Connexion
            </Link>
            <Link
              to="/signup"
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium transition duration-300"
            >
              Inscription
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-700 hover:text-blue-600 focus:outline-none"
            >
              {isOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-gray-50 px-4 py-3 space-y-3">
          <Link
            to="/"
            className="block text-gray-700 hover:text-blue-600 font-medium transition duration-300"
            onClick={() => setIsOpen(false)}
          >
            Accueil
          </Link>
          <Link
            to="/login"
            className="block text-gray-700 hover:text-blue-600 font-medium transition duration-300"
            onClick={() => setIsOpen(false)}
          >
            Connexion
          </Link>
          <Link
            to="/signup"
            className="block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium transition duration-300 text-center"
            onClick={() => setIsOpen(false)}
          >
            Inscription
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
