import React from 'react';
import { Link } from 'react-router-dom';
import { FaArrowRight, FaFileInvoice, FaCheckCircle, FaRobot } from 'react-icons/fa';

const Home: React.FC = () => {
  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Docatrust
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Automatisez l'extraction et la validation de vos documents administratifs avec la puissance de l'IA
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              to="/signup"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 font-semibold transition duration-300 flex items-center justify-center gap-2"
            >
              Commencer maintenant
              <FaArrowRight />
            </Link>
            <Link
              to="/login"
              className="bg-gray-200 text-gray-900 px-8 py-3 rounded-lg hover:bg-gray-300 font-semibold transition duration-300"
            >
              Se connecter
            </Link>
          </div>
          <img
            src="https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=500&fit=crop"
            alt="Documents"
            className="rounded-lg shadow-lg max-w-2xl mx-auto"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Pourquoi choisir Docatrust ?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition duration-300">
              <div className="flex justify-center mb-4">
                <FaRobot className="text-4xl text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
                Extraction Intelligente
              </h3>
              <p className="text-gray-600 text-center">
                Notre IA extrait automatiquement les informations clés de vos documents : SIRET, montants, dates, etc.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition duration-300">
              <div className="flex justify-center mb-4">
                <FaCheckCircle className="text-4xl text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
                Validation Automatique
              </h3>
              <p className="text-gray-600 text-center">
                Vérifiez la cohérence entre documents et détectez automatiquement les incohérences et anomalies.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-lg shadow-sm hover:shadow-md transition duration-300">
              <div className="flex justify-center mb-4">
                <FaFileInvoice className="text-4xl text-purple-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
                Multi-documents
              </h3>
              <p className="text-gray-600 text-center">
                Traitez factures, devis, attestations SIRET, RIB et bien d'autres formats de documents.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Comment ça marche ?
          </h2>
          
          <div className="grid md:grid-cols-4 gap-4 md:gap-2">
            {/* Step 1 */}
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload</h3>
              <p className="text-gray-600 text-sm">Uploadez vos documents PDF ou images</p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <FaArrowRight className="text-gray-400 text-2xl" />
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Classification</h3>
              <p className="text-gray-600 text-sm">IA identifie le type de document</p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <FaArrowRight className="text-gray-400 text-2xl" />
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Extraction</h3>
              <p className="text-gray-600 text-sm">Extraction des données via OCR</p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <FaArrowRight className="text-gray-400 text-2xl" />
            </div>

            {/* Step 4 */}
            <div className="text-center md:col-start-2">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">4</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Validation</h3>
              <p className="text-gray-600 text-sm">Vérification de cohérence</p>
            </div>

            {/* Arrow */}
            <div className="hidden md:flex items-center justify-center">
              <FaArrowRight className="text-gray-400 text-2xl" />
            </div>

            {/* Step 5 */}
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">5</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Intégration</h3>
              <p className="text-gray-600 text-sm">Export vers vos outils internes</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-blue-700">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Prêt à transformer votre gestion documentaire ?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Rejoignez les entreprises qui font confiance à Docatrust
          </p>
          <Link
            to="/signup"
            className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:bg-gray-100 font-semibold transition duration-300 inline-flex items-center gap-2"
          >
            S'inscrire gratuitement
            <FaArrowRight />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;