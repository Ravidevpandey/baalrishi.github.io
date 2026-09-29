// Entry point for interactive features. The page content itself works without JavaScript.
import { startAuth } from './auth-ui.js';

startAuth();

const page = document.body.dataset.page;
if (page === 'home') import('./reviews.js').then(m => m.initReviews());
if (page === 'account') import('./account.js').then(m => m.initAccount());
if (page === 'admin') import('./admin.js').then(m => m.initAdmin());
