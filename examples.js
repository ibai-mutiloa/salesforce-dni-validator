/**
 * Salesforce Identity Validator - JavaScript/TypeScript Examples
 *
 * Usage:
 *   // Node.js with fetch (Node 18+)
 *   node examples.js
 *
 *   // Browser - paste code in console or use in your application
 */

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = 'http://localhost:8000';
const API_VERSION = 'v1';

// ============================================================================
// TypeScript Types (optional - for TypeScript projects)
// ============================================================================

interface ValidationResponse {
  status: 'OK' | 'ERROR' | 'PARTIAL_MATCH' | 'UNKNOWN_DOCUMENT';
  confidence_score: number;
  salesforce_name: string;
  ocr_name: string;
  document_number: string | null;
  first_name_score: number;
  last_name_score: number;
  reason: string | null;
  timestamp: string;
  ocr_data?: {
    first_name: string | null;
    last_name: string | null;
    document_number: string | null;
    document_type: string | null;
    date_of_birth: string | null;
    expiration_date: string | null;
    raw_text: string | null;
  };
}

interface HealthResponse {
  status: string;
  version: string;
  azure_connected: boolean;
}

// ============================================================================
// JavaScript API Client
// ============================================================================

class IdentityValidatorClient {
  private baseUrl: string;

  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/${API_VERSION}/health`
    );

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Validate user identity against document
   */
  async validateIdentity(
    userId: string,
    firstName: string,
    lastName: string,
    documentFile: File | Blob,
    fileName: string = 'document.pdf'
  ): Promise<ValidationResponse> {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('first_name', firstName);
    formData.append('last_name', lastName);
    formData.append('document', documentFile, fileName);

    const response = await fetch(
      `${this.baseUrl}/api/${API_VERSION}/validate-identity`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        `Validation failed: ${error.detail || response.statusText}`
      );
    }

    return response.json();
  }

  /**
   * Pretty print validation result
   */
  printValidationResult(result: ValidationResponse): void {
    console.log('\n' + '='.repeat(60));
    console.log('VALIDATION RESULT');
    console.log('='.repeat(60));

    console.log(`\nStatus: ${result.status}`);
    console.log(`Confidence Score: ${result.confidence_score.toFixed(1)}%`);
    console.log(`First Name Score: ${result.first_name_score.toFixed(1)}%`);
    console.log(`Last Name Score: ${result.last_name_score.toFixed(1)}%`);

    console.log(`\nSalesforce Name: ${result.salesforce_name}`);
    console.log(`OCR Name: ${result.ocr_name}`);
    console.log(`Document Number: ${result.document_number}`);

    if (result.reason) {
      console.log(`Reason: ${result.reason}`);
    }

    console.log(`Timestamp: ${result.timestamp}`);

    if (result.ocr_data) {
      console.log('\nExtracted Document Data:');
      if (result.ocr_data.first_name)
        console.log(`  First Name: ${result.ocr_data.first_name}`);
      if (result.ocr_data.last_name)
        console.log(`  Last Name: ${result.ocr_data.last_name}`);
      if (result.ocr_data.document_number)
        console.log(`  Document Number: ${result.ocr_data.document_number}`);
      if (result.ocr_data.document_type)
        console.log(`  Document Type: ${result.ocr_data.document_type}`);
      if (result.ocr_data.date_of_birth)
        console.log(`  Date of Birth: ${result.ocr_data.date_of_birth}`);
      if (result.ocr_data.expiration_date)
        console.log(`  Expiration Date: ${result.ocr_data.expiration_date}`);
    }

    console.log('='.repeat(60) + '\n');
  }
}

// ============================================================================
// Example Functions
// ============================================================================

/**
 * Example 1: Health Check
 */
async function example1HealthCheck() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 1: Health Check');
  console.log('▶'.repeat(30));

  const client = new IdentityValidatorClient();

  try {
    const health = await client.healthCheck();
    console.log('✓ Health Status:', health.status);
    console.log('✓ Version:', health.version);
    console.log('✓ Azure Connected:', health.azure_connected);
  } catch (error) {
    console.error('✗ Error:', error.message);
    console.error(
      'Make sure the API is running: python main.py'
    );
  }
}

/**
 * Example 2: Validate Identity with Form
 */
async function example2ValidateIdentityWithForm() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 2: Validate Identity (Browser Form)');
  console.log('▶'.repeat(30));

  // This example is for browser usage
  const htmlCode = `
  <form id="validationForm">
    <input type="text" id="userId" placeholder="Salesforce User ID" required />
    <input type="text" id="firstName" placeholder="First Name" required />
    <input type="text" id="lastName" placeholder="Last Name" required />
    <input type="file" id="document" accept=".pdf,.jpg,.jpeg,.png" required />
    <button type="submit">Validate</button>
  </form>

  <div id="result"></div>

  <script>
    const client = new IdentityValidatorClient();

    document.getElementById('validationForm').addEventListener('submit', async (e) => {
      e.preventDefault();

      try {
        const result = await client.validateIdentity(
          document.getElementById('userId').value,
          document.getElementById('firstName').value,
          document.getElementById('lastName').value,
          document.getElementById('document').files[0]
        );

        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = \`
          <h2>Result: \${result.status}</h2>
          <p>Confidence: \${result.confidence_score.toFixed(1)}%</p>
          <pre>\${JSON.stringify(result, null, 2)}</pre>
        \`;
      } catch (error) {
        document.getElementById('result').innerHTML = \`<p>Error: \${error.message}</p>\`;
      }
    });
  </script>
  `;

  console.log('Browser form example HTML:');
  console.log(htmlCode);
}

/**
 * Example 3: Batch Processing
 */
async function example3BatchProcessing() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 3: Batch Processing');
  console.log('▶'.repeat(30));

  const client = new IdentityValidatorClient();

  const users = [
    { userId: '005xx000000xyz', firstName: 'Jonathan', lastName: 'Garcia' },
    { userId: '005xx000000abc', firstName: 'Maria', lastName: 'Rodriguez' },
    { userId: '005xx000000def', firstName: 'Carlos', lastName: 'Lopez' },
  ];

  const results = [];

  for (const user of users) {
    try {
      console.log(`Processing: ${user.firstName} ${user.lastName}...`);

      // In a real scenario, you'd have actual file data
      // This is just for demonstration
      const dummyFile = new Blob(['Test document'], { type: 'text/plain' });

      const result = await client.validateIdentity(
        user.userId,
        user.firstName,
        user.lastName,
        dummyFile,
        'document.txt'
      );

      results.push({
        userId: user.userId,
        name: `${user.firstName} ${user.lastName}`,
        status: result.status,
        score: result.confidence_score,
      });

      console.log(`  Status: ${result.status} (${result.confidence_score.toFixed(1)}%)`);
    } catch (error) {
      console.error(`  Error: ${error.message}`);
      results.push({
        userId: user.userId,
        name: `${user.firstName} ${user.lastName}`,
        status: 'ERROR',
        score: 0,
      });
    }
  }

  console.log('\\n' + '='.repeat(60));
  console.log('BATCH PROCESSING SUMMARY');
  console.log('='.repeat(60));

  for (const result of results) {
    const symbol = result.status === 'OK' ? '✓' : '✗';
    console.log(
      `${symbol} ${result.name.padEnd(20)} | ${result.status.padEnd(15)} | ${result.score.toFixed(1)}%`
    );
  }

  console.log('='.repeat(60));
}

/**
 * Example 4: Error Handling
 */
async function example4ErrorHandling() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 4: Error Handling');
  console.log('▶'.repeat(30));

  const client = new IdentityValidatorClient();

  // Example 4a: Missing required field
  console.log('\\nAttempting validation with missing field...');
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/${API_VERSION}/validate-identity`,
      {
        method: 'POST',
        body: new FormData(), // Empty form data - missing required fields
      }
    );

    if (!response.ok) {
      const error = await response.json();
      console.log(
        '✓ Validation error caught:',
        error.detail || response.statusText
      );
    }
  } catch (error) {
    console.error('✗ Error:', error.message);
  }
}

/**
 * Example 5: Using Async/Await
 */
async function example5AsyncAwait() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 5: Async/Await Pattern');
  console.log('▶'.repeat(30));

  const client = new IdentityValidatorClient();

  try {
    // Check health first
    const health = await client.healthCheck();
    console.log('API is healthy:', health.status);

    // Create a test file
    const testContent = 'Test Identity Document';
    const testFile = new Blob([testContent], { type: 'text/plain' });

    // Validate identity
    console.log('Validating identity...');
    const result = await client.validateIdentity(
      '005xx000000xyz',
      'Jonathan',
      'Garcia',
      testFile,
      'test_doc.txt'
    );

    client.printValidationResult(result);

    // Check result and take action
    if (result.status === 'OK') {
      console.log('✓ Identity validation successful!');
    } else if (result.status === 'PARTIAL_MATCH') {
      console.log('⚠ Manual review recommended');
    } else {
      console.log('✗ Identity validation failed');
    }
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 6: Promise-based approach
 */
function example6PromiseChain() {
  console.log('\\n' + '▶'.repeat(30));
  console.log('Example 6: Promise Chain Pattern');
  console.log('▶'.repeat(30));

  const client = new IdentityValidatorClient();

  client
    .healthCheck()
    .then((health) => {
      console.log('API Status:', health.status);
      console.log('API Version:', health.version);

      // Continue with validation
      const testFile = new Blob(['Test'], { type: 'text/plain' });
      return client.validateIdentity(
        '005xx000000xyz',
        'Jonathan',
        'Garcia',
        testFile,
        'doc.txt'
      );
    })
    .then((result) => {
      console.log('Validation complete:', result.status);
      return result;
    })
    .catch((error) => {
      console.error('Error in chain:', error.message);
    });
}

// ============================================================================
// Main - Run all examples
// ============================================================================

async function main() {
  console.log('\\n' + '█'.repeat(60));
  console.log(
    '█  Salesforce Identity Validator - JavaScript Examples'
  );
  console.log('█'.repeat(60));

  try {
    await example1HealthCheck();
    await example2ValidateIdentityWithForm();
    await example3BatchProcessing();
    await example4ErrorHandling();
    await example5AsyncAwait();
    example6PromiseChain();

    console.log('\\n' + '▶'.repeat(30));
    console.log('Examples Complete!');
    console.log('▶'.repeat(30));

    console.log('\\nTo continue working with the API:');
    console.log('  1. Access Swagger UI: http://localhost:8000/docs');
    console.log('  2. Read README.md for detailed documentation');
    console.log(
      '  3. Integrate the client into your application'
    );
  } catch (error) {
    console.error('Fatal error:', error);
  }
}

// Run examples if executed directly
if (typeof require !== 'undefined' && require.main === module) {
  main().catch(console.error);
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    IdentityValidatorClient,
    example1HealthCheck,
    example2ValidateIdentityWithForm,
    example3BatchProcessing,
    example4ErrorHandling,
    example5AsyncAwait,
    example6PromiseChain,
  };
}
