import '@testing-library/jest-dom';

describe('Background color', () => {
  it('should render with an orange background', () => {
    // The test assumes that the application under test sets the body's background-color to orange.
    // We directly check the computed style on the document body.
    expect(document.body).toHaveStyle('background-color: orange');
  });
});