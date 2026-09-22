const fs = require('fs');
const path = require('path');

describe('Background color', () => {
  it('should set the body background-color to orange in the CSS file', () => {
    const cssPath = path.resolve(__dirname, '..', 'styles.css');
    const cssContent = fs.readFileSync(cssPath, 'utf8');

    // Normalize whitespace for a flexible match
    const normalized = cssContent.replace(/\s+/g, ' ').trim();

    // Expect a rule like: body { background-color: orange; }
    expect(normalized).toMatch(/body\s*{\s*background-color:\s*orange\s*;?\s*}/i);
  });
});