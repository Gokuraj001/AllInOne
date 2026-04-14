const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
const bodyParser = require('body-parser');
require('dotenv').config();
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Configure Nodemailer
const transporter = nodemailer.createTransport({
  service: process.env.EMAIL_SERVICE || 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASSWORD
  }
});

// Verify connection
transporter.verify((error, success) => {
  if (error) {
    console.log('Email service error:', error);
  } else {
    console.log('✅ Email service is ready');
  }
});

// Contact API Endpoint
app.post('/api/contact', async (req, res) => {
  try {
    const { userName, userEmail, userComment } = req.body;

    // Validation
    if (!userName || !userEmail || !userComment) {
      return res.status(400).json({ 
        message: 'All fields are required' 
      });
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(userEmail)) {
      return res.status(400).json({ 
        message: 'Invalid email format' 
      });
    }

    // Count words
    const wordCount = userComment.trim().split(/\s+/).filter(w => w.length > 0).length;
    if (wordCount > 600) {
      return res.status(400).json({ 
        message: 'Message exceeds 600 words limit' 
      });
    }

    // Email content for admin
    const adminMailOptions = {
      from: process.env.EMAIL_USER,
      to: process.env.ADMIN_EMAIL,
      subject: `New Contact Form Submission from ${userName}`,
      html: `
        <h2>New Contact Form Submission</h2>
        <p><strong>Name:</strong> ${escapeHtml(userName)}</p>
        <p><strong>Email:</strong> ${escapeHtml(userEmail)}</p>
        <p><strong>Word Count:</strong> ${wordCount} words</p>
        <hr />
        <h3>Message:</h3>
        <p>${escapeHtml(userComment).replace(/\n/g, '<br>')}</p>
        <hr />
        <p style="color: #666; font-size: 12px;">
          This is an automated email from the ALL-IN-ONE contact form.
        </p>
      `
    };

    // Email content for user (confirmation)
    const userMailOptions = {
      from: process.env.EMAIL_USER,
      to: userEmail,
      subject: 'We received your message - ALL-IN-ONE',
      html: `
        <h2>Thank You for Contacting Us!</h2>
        <p>Hi ${escapeHtml(userName)},</p>
        <p>We have received your message and will review it shortly. 
        Our team will get back to you as soon as possible.</p>
        <hr />
        <h3>Your Message Summary:</h3>
        <p><strong>Word Count:</strong> ${wordCount} words</p>
        <hr />
        <p>Best regards,<br>ALL-IN-ONE Team</p>
        <p style="color: #666; font-size: 12px;">
          Please do not reply to this email. Use our contact form for further communication.
        </p>
      `
    };

    // Send email to admin
    await transporter.sendMail(adminMailOptions);

    // Send confirmation email to user
    await transporter.sendMail(userMailOptions);

    // Log the contact (optional - for record keeping)
    console.log(`📧 Contact form submitted by ${userName} (${userEmail})`);

    res.status(200).json({ 
      message: 'Message sent successfully',
      success: true 
    });

  } catch (error) {
    console.error('Error sending email:', error);
    res.status(500).json({ 
      message: 'Failed to send message. Please try again later.',
      error: error.message 
    });
  }
});

// HTML escape function for security
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Basic route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'contact.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ 
    message: 'An error occurred',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});