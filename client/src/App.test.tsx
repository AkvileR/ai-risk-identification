import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders the input view heading', () => {
  render(<App credentials={{ email: "test@example.com", passcode: "test" }} />);
  expect(
    screen.getByText(/EU AI Act Risk Identification/i)
  ).toBeInTheDocument();
});
