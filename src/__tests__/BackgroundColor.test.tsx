import { render } from '@testing-library/react';
import App from '../App'; // Adjust the import path as needed for your project

describe('Background color', () => {
  it('should render with an orange background', () => {
    render(<App />);
    expect(document.body).toHaveStyle('background-color: orange');
  });
});