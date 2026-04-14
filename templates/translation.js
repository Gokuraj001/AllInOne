const T = {
  en: {
    brand: 'ALL-IN-ONE',
    menuTitle: 'Navigation',
    navPricing: 'Pricing',
    navLang: 'Language',
    navPrivacy: 'Privacy Policy',
    navTerms: 'Terms & Conditions',
    navAbout: 'About Us',
    navContact: 'Contact Us',
    heroBadge: 'Free · Fast · Unlimited',
    heroLine1: 'Welcome ALL-IN-ONE',
    heroLine2: 'Tools',
    heroSub: 'ALL-IN-ONE is a platform where you can get all the tools for free!!!',
    ctaExplore: 'Explore Tools',
    ctaLearn: 'Learn More',
    scrollHint: 'Scroll',
    toolsEye: 'Our Toolkit',
    toolsTitleA: '11 Powerful Tools,',
    toolsTitleB: 'Zero Cost',
    pricingTitle: 'Coming Soon!',
    pricingMsg: "This feature will be available soon.<br>We're crafting something extraordinary for you.",
    modalClose: 'Awesome, got it!',
    modeLabel: 'Dark Mode',
    modeLabelLight: 'Light Mode',
    footerTagline: 'Your all-in-one destination for powerful, free tools. No cost, no limits.',
    footerLegal: 'Legal',
    footerCompany: 'Company',
    footerTools: 'Tools',
    footerCopy: '© 2025 ALL-IN-ONE. All rights reserved.',
    pill1: 'Free Forever',
    pill2: 'No Sign-up',
    pill3: '100% Private',
    toolAction: 'Open Tool →',
    t0n: 'Image Compress',
    t0d: 'Reduce image file sizes without losing a pixel of quality.',
    t1n: 'Image to PDF',
    t1d: 'Transform any image into a polished PDF document instantly.',
    t2n: 'Merge PDF',
    t2d: 'Combine multiple PDFs into one seamless, unified file.',
    t3n: 'Organise PDF',
    t3d: 'Reorder, rotate and manage your PDF pages with ease.',
    t4n: 'PDF to Image',
    t4d: 'Extract crisp, high-resolution images from any PDF.',
    t5n: 'PDF to Text',
    t5d: 'Convert PDF content into fully editable plain-text files.',
    t6n: 'Compress PDF',
    t6d: 'Shrink PDF sizes dramatically while keeping full quality.',
    t7n: 'Split PDF',
    t7d: 'Divide large PDFs into multiple focused documents.',
    t8n: 'Excel, Word & PPT to PDF',
    t8d: 'Convert Word, Excel, or PowerPoint files to professional PDF documents.',
    t9n: 'PDF to Excel, Word & PPT',
    t9d: 'Transform PDF files back into editable Word, Excel, or PowerPoint formats.',
    t10n: 'QR Generator',
    t10d: 'Create different types of QR codes from any URL instantly.'
  },
  es: {
    brand: 'TODO-EN-UNO',
    menuTitle: 'Navegación',
    navPricing: 'Precios',
    navLang: 'Idioma',
    navPrivacy: 'Política de Privacidad',
    navTerms: 'Términos & Condiciones',
    navAbout: 'Sobre Nosotros',
    navContact: 'Contáctenos',
    heroBadge: 'Gratis · Rápido · Ilimitado',
    heroLine1: 'Bienvenido a TODO-EN-UNO',
    heroLine2: 'Herramientas',
    heroSub: 'TODO-EN-UNO es una plataforma donde puedes obtener todas las herramientas de forma gratuita!!!',
    ctaExplore: 'Explorar Herramientas',
    ctaLearn: 'Más Información',
    scrollHint: 'Desplazar',
    toolsEye: 'Nuestro Conjunto de Herramientas',
    toolsTitleA: '11 Herramientas Poderosas,',
    toolsTitleB: 'Costo Cero',
    pricingTitle: '¡Próximamente!',
    pricingMsg: 'Esta función estará disponible pronto.<br>Estamos creando algo extraordinario para ti.',
    modalClose: '¡Genial, entendido!',
    modeLabel: 'Modo Oscuro',
    modeLabelLight: 'Modo Claro',
    footerTagline: 'Tu destino todo en uno para herramientas potentes y gratuitas. Sin costo, sin límites.',
    footerLegal: 'Legal',
    footerCompany: 'Empresa',
    footerTools: 'Herramientas',
    footerCopy: '© 2025 TODO-EN-UNO. Todos los derechos reservados.',
    pill1: 'Gratis para Siempre',
    pill2: 'Sin Registro',
    pill3: '100% Privado',
    toolAction: 'Abrir Herramienta →',
    t0n: 'Comprimir Imagen',
    t0d: 'Reduce el tamaño de los archivos de imagen sin perder calidad.',
    t1n: 'Imagen a PDF',
    t1d: 'Transforma cualquier imagen en un documento PDF pulido al instante.',
    t2n: 'Combinar PDF',
    t2d: 'Combina múltiples PDF en un solo archivo unificado.',
    t3n: 'Organizar PDF',
    t3d: 'Reordena, gira y gestiona las páginas de tus PDF con facilidad.',
    t4n: 'PDF a Imagen',
    t4d: 'Extrae imágenes nítidas y de alta resolución de cualquier PDF.',
    t5n: 'PDF a Texto',
    t5d: 'Convierte el contenido de PDF en archivos de texto plano completamente editables.',
    t6n: 'Comprimir PDF',
    t6d: 'Reduce drásticamente el tamaño de los PDF manteniendo la calidad completa.',
    t7n: 'Dividir PDF',
    t7d: 'Divide PDF grandes en múltiples documentos enfocados.',
    t8n: 'Excel, Word y PPT a PDF',
    t8d: 'Convierte archivos de Word, Excel o PowerPoint en documentos PDF profesionales.',
    t9n: 'PDF a Excel, Word y PPT',
    t9d: 'Transforma archivos PDF de nuevo en formatos editables de Word, Excel o PowerPoint.',
    t10n: 'Generador de QR',
    t10d: 'Crea códigos QR a partir de cualquier URL al instante.'
  }
  // Add other languages here if needed
};

/* Apply translations to the current document */
function applyTranslations(lang = 'en') {
  const dict = T[lang] || T.en;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      // Preserve placeholders for inputs, buttons, etc.
      if (el.tagName === 'INPUT' && el.hasAttribute('placeholder')) {
        el.placeholder = dict[key];
      } else if (el.tagName === 'IMG' && el.hasAttribute('alt')) {
        el.alt = dict[key];
      } else {
        el.textContent = dict[key];
      }
    }
  });
}

/* Language selector – called from the drawer toggle */
function setLanguage(lang) {
  localStorage.setItem('lang', lang);
  applyTranslations(lang);
}

/* Initialise on page load */
document.addEventListener('DOMContentLoaded', () => {
  const stored = localStorage.getItem('lang') || 'en';
  applyTranslations(stored);
});
