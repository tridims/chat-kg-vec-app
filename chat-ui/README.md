# Chat UI with Graph Visualization

Next.js project that combines a chat interface with graph visualization and file upload capabilities. It provides an interactive platform for users to engage in conversations, visualize data in graph format, and manage document uploads.

## Features

- **Interactive Chat Interface**: Engage in real-time conversations with an AI-powered chat system.
- **Dynamic Graph Visualization**: Visualize complex data structures with an auto-updating graph component.
- **Document Management**: Upload, view, and delete documents within the application.
- **Responsive Layout**: Utilize a resizable three-panel layout for optimal user experience.

## Technologies Used

- **Frontend**:
  - Next.js
  - React
  - TypeScript
  - Tailwind CSS
  - Radix UI components
  - React-Sigma (for graph visualization)

## Project Structure

```
src/
├── app/
│   ├── favicon.ico
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/
│   ├── chat.tsx
│   ├── dashboard.tsx
│   ├── DisplayGraph.tsx
│   ├── file_upload.tsx
│   └── graph.tsx
└── lib/
    ├── graph.ts
    └── utils.ts
```

- `app/`: Contains the main application files, including the root layout and page components.
- `components/`: Houses the main feature components and reusable UI components.
- `lib/`: Contains utility functions and shared code.

## Installation

1. Clone the repository and go to the project directory:
2. Install dependencies:
   ```
   npm install
   ```

## Usage

1. Start the development server:
   ```
   npm run dev
   ```

2. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

3. Use the chat interface in the left panel to interact with the AI system.

4. Explore the graph visualization in the middle panel to view data relationships.

5. Manage document uploads using the file upload interface in the right panel.

## API Endpoints

The application interacts with the following API endpoints:

- `/chat/completions`: POST request for chat interactions
- `/document`: GET request to fetch the list of documents, POST request to upload new documents
- `/document/:filename`: DELETE request to remove a document
- `/graph`: GET request to fetch graph data

These api is provided by the chat-rag-services.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

---

For more detailed information about using Next.js, check out the [Next.js Documentation](https://nextjs.org/docs) or try the [Learn Next.js](https://nextjs.org/learn) interactive tutorial.
