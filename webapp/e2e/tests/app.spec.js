const { test, expect } = require('@playwright/test');

test.describe('DSPy Streaming App E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://frontend:3000');
  });

  test('should load the app', async ({ page }) => {
    await expect(page).toHaveTitle(/DSPy Streaming App/);
    await expect(page.locator('h1')).toContainText('DSPy Streaming Demo');
  });

  test('should have input and button', async ({ page }) => {
    const input = page.getByTestId('question-input');
    const button = page.getByTestId('submit-button');
    
    await expect(input).toBeVisible();
    await expect(button).toBeVisible();
    await expect(button).toBeDisabled();
  });

  test('should enable button when text is entered', async ({ page }) => {
    const input = page.getByTestId('question-input');
    const button = page.getByTestId('submit-button');
    
    await input.fill('Test question');
    await expect(button).not.toBeDisabled();
  });

  test('should stream response when question is submitted', async ({ page }) => {
    const input = page.getByTestId('question-input');
    const button = page.getByTestId('submit-button');
    
    // Type a question
    await input.fill('What is JavaScript?');
    
    // Submit
    await button.click();
    
    // Button should show streaming state
    await expect(button).toContainText('Streaming...');
    await expect(button).toBeDisabled();
    
    // Wait for response to appear
    const response = page.getByTestId('response');
    await expect(response).toBeVisible({ timeout: 10000 });
    
    // Response should contain text
    await expect(response).toContainText(/Response:/);
    
    // Button should return to normal state
    await expect(button).toContainText('Ask');
    await expect(button).not.toBeDisabled();
  });

  test('should handle multiple questions', async ({ page }) => {
    const input = page.getByTestId('question-input');
    const button = page.getByTestId('submit-button');
    
    // First question
    await input.fill('First question');
    await button.click();
    await expect(page.getByTestId('response')).toBeVisible({ timeout: 10000 });
    
    // Clear and ask second question
    await input.clear();
    await input.fill('Second question');
    await button.click();
    
    // Should show new response
    await expect(button).toContainText('Streaming...');
    await expect(page.getByTestId('response')).toBeVisible();
  });

  test('should handle empty input gracefully', async ({ page }) => {
    const input = page.getByTestId('question-input');
    const button = page.getByTestId('submit-button');
    
    // Try to submit empty
    await input.clear();
    await expect(button).toBeDisabled();
    
    // Add and remove text
    await input.fill('test');
    await expect(button).not.toBeDisabled();
    await input.clear();
    await expect(button).toBeDisabled();
  });
});