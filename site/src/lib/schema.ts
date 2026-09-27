import settings from '../content/settings.json';

export const serviceSchema = (name: string, description: string) => ({
  '@context': 'https://schema.org',
  '@type': 'Service',
  name,
  description,
  areaServed: 'Worldwide',
  provider: { '@type': 'Organization', name: settings.site_name, url: settings.site_url, email: settings.contact_email },
});

export const faqSchema = (items: { question: string; answer: string }[]) => ({
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: items.map((f) => ({ '@type': 'Question', name: f.question, acceptedAnswer: { '@type': 'Answer', text: f.answer } })),
});

export const organizationSchema = () => ({
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: settings.site_name,
  url: settings.site_url,
  logo: new URL('/logo.svg', settings.site_url).href,
  email: settings.contact_email,
  areaServed: 'Worldwide',
  founder: { '@type': 'Person', name: 'April' },
  sameAs: [settings.linkedin_url].filter(Boolean),
});
