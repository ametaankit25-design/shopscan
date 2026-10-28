// src/components/Footer.jsx
import {
  Compass,
  Send,
  MessageCircle,
} from 'lucide-react';
import { useState } from 'react';
import { useToast } from '../context/ToastContext';

const FacebookIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const TwitterIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const InstagramIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>
    <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
    <line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
  </svg>
);

export default function Footer() {
  const [email, setEmail] = useState('');
  const [agreed, setAgreed] = useState(true);
  const toast = useToast();

  const handleSubscribe = (e) => {
    e.preventDefault();
    if (!email) return;
    toast('Thank you for subscribing to our newsletter!', 'success');
    setEmail('');
  };

  return (
    <footer className="vazhi-footer">
      <div className="vazhi-container footer-content">
        {/* Brand Column */}
        <div className="footer-col brand-col">
          <div className="vazhi-logo footer-logo">
            <div className="logo-badge">
              <Compass size={18} />
            </div>
            <span className="logo-text">Vazhi</span>
          </div>
          <p className="footer-bio">
            Discover premier businesses, top-rated destinations, local dining, and exceptional services curated for discerning travelers and locals.
          </p>
          <div className="footer-social-circles">
            <a href="#wa" aria-label="WhatsApp" className="social-pill whatsapp">
              <MessageCircle size={15} />
            </a>
            <a href="#fb" aria-label="Facebook" className="social-pill facebook">
              <FacebookIcon />
            </a>
            <a href="#x" aria-label="X Twitter" className="social-pill twitter">
              <TwitterIcon />
            </a>
            <a href="#ig" aria-label="Instagram" className="social-pill instagram">
              <InstagramIcon />
            </a>
          </div>
        </div>

        {/* Quick Links */}
        <div className="footer-col">
          <h4 className="footer-heading">Quick Links</h4>
          <ul className="footer-links">
            <li><a href="#signin">Sign In</a></li>
            <li><a href="#profile">My Profile</a></li>
            <li><a href="#reviews">My Reviews</a></li>
            <li><a href="#advertise">Advertise with Us</a></li>
            <li><a href="#partner">Partner Program</a></li>
            <li><a href="#careers">Careers</a></li>
          </ul>
        </div>

        {/* Support */}
        <div className="footer-col">
          <h4 className="footer-heading">Support</h4>
          <ul className="footer-links">
            <li><a href="#faqs">Frequent FAQ's</a></li>
            <li><a href="#privacy">Privacy Policy</a></li>
            <li><a href="#terms">Terms of Service</a></li>
            <li><a href="#guide">Listing Guide</a></li>
            <li><a href="#accessibility">Accessibility</a></li>
          </ul>
        </div>

        {/* Newsletter Subscription */}
        <div className="footer-col newsletter-col">
          <h4 className="footer-heading">Newsletter Subscription</h4>
          <p className="newsletter-text">
            Stay updated with newest business openings, hand-picked listings and exclusive city insights.
          </p>

          <form onSubmit={handleSubscribe} className="newsletter-form">
            <div className="newsletter-input-wrap">
              <input
                type="email"
                placeholder="Enter Your Mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="newsletter-input"
              />
              <button type="submit" className="newsletter-submit-btn" aria-label="Subscribe">
                <Send size={15} />
              </button>
            </div>
            <label className="newsletter-consent">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
              />
              <span>I agree with the terms and conditions</span>
            </label>
          </form>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="footer-bottom">
        <div className="vazhi-container footer-bottom-content">
          <p className="copyright-text">
            © {new Date().getFullYear()} Vazhi All Rights Reserved.
          </p>
          <div className="payment-badges">
            <span className="pay-tag">Mastercard</span>
            <span className="pay-tag">VISA</span>
            <span className="pay-tag">AmEx</span>
            <span className="pay-tag">Apple Pay</span>
            <span className="pay-tag">PayPal</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
