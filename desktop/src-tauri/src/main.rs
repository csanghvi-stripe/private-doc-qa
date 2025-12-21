#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader, Write};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::State;

// Shared state for Python process
struct Backend {
    process: Mutex<Option<Child>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Document {
    name: String,
    path: String,
    chunks: i32,
    status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Source {
    document: String,
    page: Option<i32>,
    score: f64,
    snippet: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct InitResponse {
    ready: bool,
    documents: Vec<Document>,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnswerResponse {
    answer: String,
    sources: Vec<Source>,
    confidence: f64,
}

#[derive(Debug, Serialize, Deserialize)]
struct BackendRequest {
    command: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    question: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    paths: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct BackendResponse {
    success: bool,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

fn send_to_backend(backend: &State<Backend>, request: BackendRequest) -> Result<BackendResponse, String> {
    let mut proc_guard = backend.process.lock().map_err(|e| e.to_string())?;
    
    let child = proc_guard.as_mut().ok_or("Backend not started")?;
    
    // Write request
    let stdin = child.stdin.as_mut().ok_or("No stdin")?;
    let request_json = serde_json::to_string(&request).map_err(|e| e.to_string())?;
    writeln!(stdin, "{}", request_json).map_err(|e| e.to_string())?;
    stdin.flush().map_err(|e| e.to_string())?;
    
    // Read response
    let stdout = child.stdout.as_mut().ok_or("No stdout")?;
    let mut reader = BufReader::new(stdout);
    let mut line = String::new();
    reader.read_line(&mut line).map_err(|e| e.to_string())?;
    
    serde_json::from_str(&line).map_err(|e| format!("Parse error: {} - Response: {}", e, line))
}

#[tauri::command]
fn init_backend(backend: State<Backend>) -> Result<InitResponse, String> {
    // Start Python process
    let project_root = std::env::current_dir()
        .map_err(|e| e.to_string())?
        .parent()
        .ok_or("No parent dir")?
        .parent()
        .ok_or("No grandparent dir")?
        .to_path_buf();
    
    let script_path = project_root.join("backend_server.py");
    
    println!("Starting backend: python3 {} --json-mode", script_path.display());
    
    let child = Command::new("python3")
        .arg(&script_path)
        .arg("--json-mode")
        .current_dir(&project_root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|e| format!("Failed to start Python: {}", e))?;
    
    // Store process
    {
        let mut proc = backend.process.lock().map_err(|e| e.to_string())?;
        *proc = Some(child);
    }
    
    // Send init command
    let response = send_to_backend(&backend, BackendRequest {
        command: "init".to_string(),
        question: None,
        paths: None,
        name: None,
    })?;
    
    if response.success {
        let data = response.data.unwrap_or(serde_json::json!({}));
        let documents: Vec<Document> = serde_json::from_value(
            data.get("documents").cloned().unwrap_or(serde_json::json!([]))
        ).unwrap_or_default();
        
        Ok(InitResponse {
            ready: true,
            documents,
        })
    } else {
        Err(response.error.unwrap_or("Init failed".to_string()))
    }
}

#[tauri::command]
fn add_documents(paths: Vec<String>, backend: State<Backend>) -> Result<Vec<Document>, String> {
    let response = send_to_backend(&backend, BackendRequest {
        command: "add_documents".to_string(),
        question: None,
        paths: Some(paths),
        name: None,
    })?;
    
    if response.success {
        let data = response.data.unwrap_or(serde_json::json!({}));
        let documents: Vec<Document> = serde_json::from_value(
            data.get("documents").cloned().unwrap_or(serde_json::json!([]))
        ).unwrap_or_default();
        Ok(documents)
    } else {
        Err(response.error.unwrap_or("Failed to add documents".to_string()))
    }
}

#[tauri::command]
fn ask_question(question: String, backend: State<Backend>) -> Result<AnswerResponse, String> {
    let response = send_to_backend(&backend, BackendRequest {
        command: "ask".to_string(),
        question: Some(question),
        paths: None,
        name: None,
    })?;
    
    if response.success {
        let data = response.data.unwrap_or(serde_json::json!({}));
        Ok(AnswerResponse {
            answer: data.get("answer")
                .and_then(|v| v.as_str())
                .unwrap_or("No answer")
                .to_string(),
            sources: serde_json::from_value(
                data.get("sources").cloned().unwrap_or(serde_json::json!([]))
            ).unwrap_or_default(),
            confidence: data.get("confidence")
                .and_then(|v| v.as_f64())
                .unwrap_or(0.0),
        })
    } else {
        Err(response.error.unwrap_or("Failed to get answer".to_string()))
    }
}

#[tauri::command]
fn remove_document(name: String, backend: State<Backend>) -> Result<(), String> {
    let response = send_to_backend(&backend, BackendRequest {
        command: "remove_document".to_string(),
        question: None,
        paths: None,
        name: Some(name),
    })?;
    
    if response.success {
        Ok(())
    } else {
        Err(response.error.unwrap_or("Failed to remove".to_string()))
    }
}

#[tauri::command]
fn record_and_transcribe(backend: State<Backend>) -> Result<String, String> {
    let response = send_to_backend(&backend, BackendRequest {
        command: "voice_input".to_string(),
        question: None,
        paths: None,
        name: None,
    })?;
    
    if response.success {
        let data = response.data.unwrap_or(serde_json::json!({}));
        Ok(data.get("transcription")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string())
    } else {
        Err(response.error.unwrap_or("Voice input failed".to_string()))
    }
}

fn main() {
    tauri::Builder::default()
        .manage(Backend {
            process: Mutex::new(None),
        })
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            init_backend,
            add_documents,
            ask_question,
            remove_document,
            record_and_transcribe,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}