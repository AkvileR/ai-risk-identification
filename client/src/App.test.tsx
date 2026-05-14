import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the input view heading', () => {
  render(<App />);
  expect(
    screen.getByText(/EU AI Act Risk Identification/i)
  ).toBeInTheDocument();
});
