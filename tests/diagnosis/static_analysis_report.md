================================================================================
异步代码静态分析报告
================================================================================

## 统计信息
- 分析文件数: 275
- 异步函数数: 329
- 潜在阻塞调用: 2063
- 分析错误: 2

## 异步函数列表

### diagnosis\e2e_diagnosis.py
  - Line 71: `test_normal_mode_flow` (await: 3)
    ⚠️  阻塞调用: json.loads (行 91, low)
    ⚠️  阻塞调用: data.get (行 93, high)
    ⚠️  阻塞调用: json.dumps (行 123, low)
    ⚠️  阻塞调用: json.loads (行 141, low)
    ⚠️  阻塞调用: data.get (行 142, high)
    ⚠️  阻塞调用: data.get (行 165, high)
  - Line 191: `test_plan_mode_flow` (await: 5)
    ⚠️  阻塞调用: json.loads (行 208, low)
    ⚠️  阻塞调用: data.get (行 210, high)
    ⚠️  阻塞调用: json.dumps (行 222, low)
    ⚠️  阻塞调用: json.loads (行 239, low)
    ⚠️  阻塞调用: data.get (行 240, high)
    ⚠️  阻塞调用: data.get (行 258, high)
    ⚠️  阻塞调用: json.dumps (行 276, low)
    ⚠️  阻塞调用: json.loads (行 290, low)
    ⚠️  阻塞调用: data.get (行 291, high)
    ⚠️  阻塞调用: data.get (行 310, high)
  - Line 336: `test_error_handling` (await: 3)
    ⚠️  阻塞调用: json.dumps (行 354, low)
    ⚠️  阻塞调用: json.loads (行 363, low)
    ⚠️  阻塞调用: data.get (行 364, high)
  - Line 399: `run_all_tests` (await: 5)
    ⚠️  阻塞调用: asyncio.sleep (行 410, high)
    ⚠️  阻塞调用: asyncio.sleep (行 417, high)
  - Line 516: `main` (await: 1)
    ⚠️  阻塞调用: open (行 540, high)
    ⚠️  阻塞调用: f.write (行 541, high)

### diagnosis\performance_tester.py
  - Line 68: `test_connection_latency` (await: 1)
    ⚠️  阻塞调用: asyncio.sleep (行 80, high)
  - Line 101: `test_message_roundtrip` (await: 3)
    ⚠️  阻塞调用: json.loads (行 110, low)
    ⚠️  阻塞调用: init_data.get (行 112, high)
    ⚠️  阻塞调用: json.dumps (行 128, low)
  - Line 155: `test_concurrent_connections` (await: 1)
  - Line 163: `connect_and_test` (await: 2)
    ⚠️  阻塞调用: json.loads (行 172, low)
    ⚠️  阻塞调用: data.get (行 174, high)
    ⚠️  阻塞调用: json.dumps (行 177, low)
  - Line 215: `test_chain_generation_performance` (await: 3)
    ⚠️  阻塞调用: json.dumps (行 228, low)
    ⚠️  阻塞调用: json.loads (行 244, low)
    ⚠️  阻塞调用: data.get (行 245, high)
  - Line 292: `run_all_tests` (await: 5)
    ⚠️  阻塞调用: result.details.get (行 302, high)
    ⚠️  阻塞调用: result.details.get (行 309, high)
    ⚠️  阻塞调用: result.details.get (行 316, high)
    ⚠️  阻塞调用: result.details.get (行 323, high)
    ⚠️  阻塞调用: result.details.get (行 330, high)
  - Line 393: `main` (await: 1)
    ⚠️  阻塞调用: open (行 419, high)
    ⚠️  阻塞调用: f.write (行 420, high)

### diagnosis\run_diagnosis.py
  - Line 67: `test_connection` (无await)

### src\flood_decision_agent\agents\decision_chain\chain_generator.py
  - Line 89: `generate` (await: 4)
    ⚠️  阻塞调用: intent.goal.get (行 209, high)
  - Line 283: `generate_from_plan` (await: 4)
  - Line 445: `generate_from_spec` (无await)

### src\flood_decision_agent\agents\decision_chain\generator.py
  - Line 104: `initialize_mcp` (await: 2)
  - Line 139: `_cache_mcp_tools` (无await)
    ⚠️  阻塞调用: tool.get (行 163, high)

### src\flood_decision_agent\agents\task_executor\executor.py
  - Line 96: `initialize_mcp` (await: 2)
  - Line 131: `_cache_mcp_tools` (无await)
    ⚠️  阻塞调用: tool.get (行 155, high)
  - Line 236: `_execute_mcp_tool` (await: 1)
    ⚠️  阻塞调用: tool_spec.get (行 251, high)
    ⚠️  阻塞调用: tool_spec.get (行 252, high)
  - Line 343: `_process_async` (await: 1)

### src\flood_decision_agent\agents\task_executor\mcp_integration.py
  - Line 41: `initialize` (await: 2)
  - Line 95: `_register_mcp_tools_to_registry` (无await)
  - Line 138: `handler` (await: 1)
  - Line 186: `execute_mcp_tool` (await: 1)
  - Line 244: `close` (await: 1)
  - Line 286: `initialize_mcp` (await: 1)
  - Line 326: `execute_task` (await: 1)
  - Line 356: `close` (await: 1)
  - Line 364: `setup_mcp_for_executor` (await: 1)

### src\flood_decision_agent\agents\task_executor\streaming_executor.py
  - Line 108: `execute` (await: 1)
    ⚠️  阻塞调用: self._get_ready_tasks (行 163, high)
    ⚠️  阻塞调用: result.get (行 214, high)
    ⚠️  阻塞调用: result.get (行 216, high)
    ⚠️  阻塞调用: result.get (行 220, high)
    ⚠️  阻塞调用: result.get (行 239, high)
  - Line 314: `_execute_task` (await: 1)
    ⚠️  阻塞调用: node.metadata.get (行 333, high)
    ⚠️  阻塞调用: tool.get (行 336, high)
    ⚠️  阻塞调用: tool.get (行 338, high)
    ⚠️  阻塞调用: tool.get (行 339, high)
    ⚠️  阻塞调用: tool.get (行 340, high)

### src\flood_decision_agent\infrastructure\llm\client.py
  - Line 15: `chat` (无await)
  - Line 20: `stream_chat` (无await)

### src\flood_decision_agent\infrastructure\llm\kimi_client.py
  - Line 79: `chat` (无await)
    ⚠️  阻塞调用: kwargs.get (行 88, high)
    ⚠️  阻塞调用: kwargs.get (行 89, high)
  - Line 95: `stream_chat` (无await)
    ⚠️  阻塞调用: kwargs.get (行 104, high)
    ⚠️  阻塞调用: kwargs.get (行 105, high)

### src\flood_decision_agent\mcp\adapters\tool_adapter.py
  - Line 34: `execute` (await: 1)
  - Line 147: `execute` (无await)
  - Line 189: `execute` (await: 2)

### src\flood_decision_agent\mcp\clients\base.py
  - Line 45: `connect` (await: 6)
    ⚠️  阻塞调用: platform.system (行 49, high)
  - Line 83: `_cleanup` (await: 2)
  - Line 97: `_fetch_tools` (await: 1)
  - Line 116: `call_tool` (await: 1)
    ⚠️  阻塞调用: json.loads (行 128, low)
  - Line 136: `close` (await: 1)
  - Line 244: `connect_all` (await: 1)
  - Line 273: `call_tool` (await: 1)
  - Line 281: `call_tool_auto` (await: 1)
  - Line 289: `close_all` (await: 1)

### src\flood_decision_agent\mcp\clients\filesystem.py
  - Line 19: `write_planning_markdown` (await: 1)
  - Line 38: `read_planning_file` (await: 1)
  - Line 53: `list_plans` (await: 1)
  - Line 64: `write_data_json` (await: 1)
  - Line 81: `read_data_json` (await: 1)

### src\flood_decision_agent\mcp\core\client.py
  - Line 109: `connect` (await: 2)
  - Line 131: `disconnect` (await: 1)
  - Line 145: `call_tool` (await: 2)
    ⚠️  阻塞调用: self.send_request (行 184, high)
    ⚠️  阻塞调用: asyncio.sleep (行 202, high)
  - Line 223: `_fetch_tools` (await: 1)
  - Line 233: `_do_connect` (无await)
  - Line 238: `_do_disconnect` (无await)
  - Line 243: `send_request` (无await)
  - Line 248: `_do_fetch_tools` (无await)
  - Line 252: `__aenter__` (await: 1)
  - Line 257: `__aexit__` (await: 1)
  - Line 308: `connect_all` (await: 1)
  - Line 323: `disconnect_all` (await: 1)
  - Line 338: `call_tool` (await: 1)
    ⚠️  阻塞调用: self._clients.get (行 354, high)
  - Line 364: `call_tool_auto` (await: 1)

### src\flood_decision_agent\mcp\core\server.py
  - Line 153: `call_tool` (await: 1)
  - Line 201: `initialize` (await: 1)
  - Line 218: `shutdown` (await: 1)
  - Line 238: `_on_initialize` (无await)
  - Line 243: `_on_shutdown` (无await)
  - Line 248: `run` (无await)

### src\flood_decision_agent\mcp\core\session.py
  - Line 149: `initialize` (无await)
  - Line 176: `close` (await: 2)
  - Line 208: `send_request` (await: 2)
    ⚠️  阻塞调用: self._do_send_request (行 241, high)
  - Line 259: `handle_response` (无await)
    ⚠️  阻塞调用: self._pending_requests.get (行 270, high)
  - Line 301: `_emit` (await: 1)
    ⚠️  阻塞调用: self._handlers.get (行 303, high)
  - Line 313: `_do_send_request` (无await)
  - Line 318: `_heartbeat_loop` (await: 2)
    ⚠️  阻塞调用: asyncio.sleep (行 322, high)
  - Line 330: `_send_heartbeat` (无await)
  - Line 335: `_cleanup_loop` (await: 2)
    ⚠️  阻塞调用: asyncio.sleep (行 339, high)
  - Line 346: `_cleanup_expired_requests` (无await)
  - Line 361: `__aenter__` (await: 1)
  - Line 366: `__aexit__` (await: 1)

### src\flood_decision_agent\mcp\core\transport.py
  - Line 81: `connect` (await: 1)
  - Line 101: `close` (await: 1)
  - Line 114: `send` (await: 1)
    ⚠️  阻塞调用: json.dumps (行 132, low)
  - Line 149: `receive` (await: 1)
  - Line 164: `receive_messages` (await: 1)
    ⚠️  阻塞调用: json.loads (行 178, low)
    ⚠️  阻塞调用: message_dict.get (行 180, high)
    ⚠️  阻塞调用: message_dict.get (行 181, high)
    ⚠️  阻塞调用: message_dict.get (行 182, high)
  - Line 193: `_do_connect` (无await)
  - Line 198: `_do_close` (无await)
  - Line 203: `_do_send` (无await)
  - Line 208: `_do_receive` (无await)
  - Line 212: `__aenter__` (await: 1)
  - Line 217: `__aexit__` (await: 1)
  - Line 235: `_do_connect` (无await)
  - Line 255: `_do_close` (await: 1)
    ⚠️  阻塞调用: self._writer.close (行 258, high)
    ⚠️  阻塞调用: self._writer.wait_closed (行 260, high)
  - Line 264: `_do_send` (无await)
    ⚠️  阻塞调用: sys.stdout.buffer.write (行 271, high)
    ⚠️  阻塞调用: sys.stdout.buffer.write (行 272, high)
  - Line 275: `_do_receive` (await: 2)
    ⚠️  阻塞调用: self._reader.readline (行 283, high)
    ⚠️  阻塞调用: self._reader.readexactly (行 302, high)
  - Line 330: `_do_connect` (无await)
  - Line 334: `_do_close` (无await)
  - Line 338: `_do_send` (await: 1)
  - Line 342: `_do_receive` (await: 1)
    ⚠️  阻塞调用: self._receive_queue.get (行 347, high)

### src\flood_decision_agent\mcp\servers\decision_chain_server.py
  - Line 150: `list_tools` (无await)
  - Line 351: `call_tool` (await: 9)
    ⚠️  阻塞调用: _handle_read_plan (行 359, high)
    ⚠️  阻塞调用: _handle_read_spec (行 365, high)
    ⚠️  阻塞调用: json.dumps (行 379, low)
  - Line 389: `_handle_create_plan` (无await)
    ⚠️  阻塞调用: args.get (行 396, high)
    ⚠️  阻塞调用: args.get (行 397, high)
    ⚠️  阻塞调用: open (行 425, high)
    ⚠️  阻塞调用: f.write (行 426, high)
    ⚠️  阻塞调用: json.dumps (行 430, low)
  - Line 440: `_handle_read_plan` (无await)
    ⚠️  阻塞调用: open (行 450, high)
    ⚠️  阻塞调用: f.read (行 451, high)
    ⚠️  阻塞调用: json.dumps (行 458, low)
  - Line 470: `_handle_update_plan` (无await)
    ⚠️  阻塞调用: open (行 483, high)
    ⚠️  阻塞调用: f.read (行 484, high)
    ⚠️  阻塞调用: open (行 490, high)
    ⚠️  阻塞调用: f.write (行 491, high)
    ⚠️  阻塞调用: json.dumps (行 495, low)
  - Line 506: `_handle_create_spec` (无await)
    ⚠️  阻塞调用: args.get (行 512, high)
    ⚠️  阻塞调用: args.get (行 513, high)
    ⚠️  阻塞调用: args.get (行 514, high)
    ⚠️  阻塞调用: args.get (行 515, high)
    ⚠️  阻塞调用: open (行 535, high)
    ⚠️  阻塞调用: f.write (行 536, high)
    ⚠️  阻塞调用: open (行 548, high)
    ⚠️  阻塞调用: f.write (行 549, high)
    ⚠️  阻塞调用: open (行 563, high)
    ⚠️  阻塞调用: f.write (行 564, high)
    ⚠️  阻塞调用: json.dumps (行 569, low)
  - Line 580: `_handle_read_spec` (无await)
    ⚠️  阻塞调用: open (行 590, high)
    ⚠️  阻塞调用: f.read (行 591, high)
    ⚠️  阻塞调用: json.dumps (行 598, low)
  - Line 609: `_handle_update_spec` (无await)
    ⚠️  阻塞调用: open (行 622, high)
    ⚠️  阻塞调用: f.read (行 623, high)
    ⚠️  阻塞调用: open (行 629, high)
    ⚠️  阻塞调用: f.write (行 630, high)
    ⚠️  阻塞调用: json.dumps (行 634, low)
  - Line 645: `_handle_list_plans` (无await)
    ⚠️  阻塞调用: args.get (行 647, high)
    ⚠️  阻塞调用: open (行 660, high)
    ⚠️  阻塞调用: f.readline (行 661, high)
    ⚠️  阻塞调用: json.dumps (行 681, low)
  - Line 689: `_handle_list_specs` (无await)
    ⚠️  阻塞调用: json.dumps (行 714, low)
  - Line 722: `_handle_delete_document` (无await)
    ⚠️  阻塞调用: json.dumps (行 736, low)
  - Line 815: `main` (await: 1)
    ⚠️  阻塞调用: platform.system (行 822, high)
    ⚠️  阻塞调用: server.run (行 828, high)

### src\flood_decision_agent\mcp\servers\document_server.py
  - Line 51: `list_tools` (无await)
  - Line 139: `call_tool` (await: 4)
    ⚠️  阻塞调用: _handle_read_docx_content (行 147, high)
    ⚠️  阻塞调用: json.dumps (行 157, low)
  - Line 165: `_handle_docx_to_markdown` (无await)
    ⚠️  阻塞调用: json.dumps (行 170, low)
    ⚠️  阻塞调用: args.get (行 177, high)
    ⚠️  阻塞调用: args.get (行 178, high)
    ⚠️  阻塞调用: open (行 245, high)
    ⚠️  阻塞调用: f.write (行 246, high)
    ⚠️  阻塞调用: json.dumps (行 250, low)
  - Line 303: `_handle_read_docx_content` (无await)
    ⚠️  阻塞调用: json.dumps (行 308, low)
    ⚠️  阻塞调用: json.dumps (行 339, low)
  - Line 349: `_handle_list_documents` (无await)
    ⚠️  阻塞调用: args.get (行 351, high)
    ⚠️  阻塞调用: args.get (行 352, high)
    ⚠️  阻塞调用: json.dumps (行 376, low)
  - Line 386: `_handle_create_sample_docx` (无await)
    ⚠️  阻塞调用: json.dumps (行 391, low)
    ⚠️  阻塞调用: args.get (行 397, high)
    ⚠️  阻塞调用: args.get (行 398, high)
    ⚠️  阻塞调用: para.add_run (行 419, high)
    ⚠️  阻塞调用: para.add_run (行 420, high)
    ⚠️  阻塞调用: para.add_run (行 421, high)
    ⚠️  阻塞调用: para.add_run (行 422, high)
    ⚠️  阻塞调用: para.add_run (行 423, high)
    ⚠️  阻塞调用: json.dumps (行 456, low)
  - Line 466: `main` (await: 1)
    ⚠️  阻塞调用: server.run (行 473, high)

### src\flood_decision_agent\mcp\servers\filesystem_server.py
  - Line 56: `list_tools` (无await)
  - Line 196: `call_tool` (await: 7)
    ⚠️  阻塞调用: _handle_write_planning (行 202, high)
    ⚠️  阻塞调用: _handle_read_planning (行 204, high)
    ⚠️  阻塞调用: _handle_write_data_json (行 212, high)
    ⚠️  阻塞调用: _handle_read_data_json (行 214, high)
    ⚠️  阻塞调用: json.dumps (行 220, low)
  - Line 227: `_handle_write_planning` (无await)
    ⚠️  阻塞调用: args.get (行 231, high)
    ⚠️  阻塞调用: args.get (行 232, high)
    ⚠️  阻塞调用: open (行 266, high)
    ⚠️  阻塞调用: f.write (行 267, high)
    ⚠️  阻塞调用: json.dumps (行 271, low)
  - Line 281: `_handle_read_planning` (无await)
    ⚠️  阻塞调用: args.get (行 284, high)
    ⚠️  阻塞调用: open (行 300, high)
    ⚠️  阻塞调用: f.read (行 301, high)
    ⚠️  阻塞调用: json.dumps (行 333, low)
  - Line 337: `_handle_list_plans` (无await)
    ⚠️  阻塞调用: args.get (行 339, high)
    ⚠️  阻塞调用: args.get (行 340, high)
    ⚠️  阻塞调用: json.dumps (行 362, low)
  - Line 370: `_handle_append_to_plan` (无await)
    ⚠️  阻塞调用: open (行 381, high)
    ⚠️  阻塞调用: f.write (行 382, high)
    ⚠️  阻塞调用: f.write (行 383, high)
    ⚠️  阻塞调用: f.write (行 384, high)
    ⚠️  阻塞调用: json.dumps (行 388, low)
  - Line 396: `_handle_delete_plan` (无await)
    ⚠️  阻塞调用: json.dumps (行 409, low)
  - Line 416: `_handle_write_data_json` (无await)
    ⚠️  阻塞调用: args.get (行 420, high)
    ⚠️  阻塞调用: open (行 428, high)
    ⚠️  阻塞调用: json.dumps (行 433, low)
  - Line 441: `_handle_read_data_json` (无await)
    ⚠️  阻塞调用: open (行 451, high)
    ⚠️  阻塞调用: json.dumps (行 456, low)
  - Line 463: `main` (await: 1)
    ⚠️  阻塞调用: server.run (行 476, high)

### src\flood_decision_agent\mcp\servers\hydrology_server.py
  - Line 212: `list_tools` (无await)
  - Line 386: `call_tool` (await: 7)
    ⚠️  阻塞调用: json.dumps (行 408, low)
  - Line 416: `_handle_list_models` (无await)
    ⚠️  阻塞调用: json.dumps (行 428, low)
  - Line 436: `_handle_get_model_info` (无await)
    ⚠️  阻塞调用: json.dumps (行 470, low)
  - Line 481: `_handle_run_rainfall_runoff` (无await)
    ⚠️  阻塞调用: args.get (行 486, high)
    ⚠️  阻塞调用: args.get (行 487, high)
    ⚠️  阻塞调用: args.get (行 488, high)
    ⚠️  阻塞调用: args.get (行 489, high)
    ⚠️  阻塞调用: model.run (行 492, high)
    ⚠️  阻塞调用: json.dumps (行 496, low)
  - Line 509: `_handle_run_flood_routing` (无await)
    ⚠️  阻塞调用: args.get (行 514, high)
    ⚠️  阻塞调用: args.get (行 515, high)
    ⚠️  阻塞调用: args.get (行 516, high)
    ⚠️  阻塞调用: args.get (行 517, high)
    ⚠️  阻塞调用: model.run (行 520, high)
    ⚠️  阻塞调用: json.dumps (行 524, low)
  - Line 538: `_handle_run_reservoir_dispatch` (无await)
    ⚠️  阻塞调用: args.get (行 543, high)
    ⚠️  阻塞调用: args.get (行 544, high)
    ⚠️  阻塞调用: args.get (行 545, high)
    ⚠️  阻塞调用: args.get (行 546, high)
    ⚠️  阻塞调用: args.get (行 547, high)
    ⚠️  阻塞调用: model.run (行 550, high)
    ⚠️  阻塞调用: json.dumps (行 554, low)
  - Line 568: `_handle_calculate_dispatch_plan` (无await)
    ⚠️  阻塞调用: args.get (行 570, high)
    ⚠️  阻塞调用: args.get (行 571, high)
    ⚠️  阻塞调用: args.get (行 572, high)
    ⚠️  阻塞调用: model.run (行 580, high)
    ⚠️  阻塞调用: current_state.get (行 582, high)
    ⚠️  阻塞调用: constraints.get (行 583, high)
    ⚠️  阻塞调用: constraints.get (行 584, high)
    ⚠️  阻塞调用: json.dumps (行 599, low)
  - Line 607: `_handle_validate_safety` (无await)
    ⚠️  阻塞调用: args.get (行 609, high)
    ⚠️  阻塞调用: args.get (行 610, high)
    ⚠️  阻塞调用: dispatch_plan.get (行 616, high)
    ⚠️  阻塞调用: dispatch_plan.get (行 626, high)
    ⚠️  阻塞调用: json.dumps (行 634, low)
    ⚠️  阻塞调用: dispatch_plan.get (行 639, high)
  - Line 645: `main` (await: 1)
    ⚠️  阻塞调用: server.run (行 650, high)

### src\flood_decision_agent\mcp\servers\rainfall_server.py
  - Line 123: `list_tools` (无await)
  - Line 236: `call_tool` (await: 5)
    ⚠️  阻塞调用: json.dumps (行 254, low)
  - Line 263: `_handle_current_rainfall` (await: 2)
    ⚠️  阻塞调用: args.get (行 266, high)
    ⚠️  阻塞调用: json.dumps (行 275, low)
    ⚠️  阻塞调用: _fetch_openweather_current (行 279, high)
    ⚠️  阻塞调用: json.dumps (行 286, low)
  - Line 289: `_handle_rainfall_forecast` (await: 2)
    ⚠️  阻塞调用: args.get (行 292, high)
    ⚠️  阻塞调用: args.get (行 293, high)
    ⚠️  阻塞调用: json.dumps (行 301, low)
    ⚠️  阻塞调用: _fetch_openweather_forecast (行 305, high)
    ⚠️  阻塞调用: json.dumps (行 312, low)
  - Line 315: `_handle_hourly_rainfall` (await: 2)
    ⚠️  阻塞调用: args.get (行 318, high)
    ⚠️  阻塞调用: args.get (行 319, high)
    ⚠️  阻塞调用: json.dumps (行 327, low)
    ⚠️  阻塞调用: _fetch_openweather_hourly (行 331, high)
    ⚠️  阻塞调用: json.dumps (行 338, low)
  - Line 341: `_handle_rainfall_by_coords` (await: 2)
    ⚠️  阻塞调用: args.get (行 345, high)
    ⚠️  阻塞调用: json.dumps (行 353, low)
    ⚠️  阻塞调用: _fetch_openweather_by_coords (行 357, high)
    ⚠️  阻塞调用: json.dumps (行 364, low)
  - Line 367: `_handle_check_api_status` (无await)
    ⚠️  阻塞调用: json.dumps (行 394, low)
  - Line 399: `_fetch_openweather_current` (await: 2)
    ⚠️  阻塞调用: session.get (行 413, high)
    ⚠️  阻塞调用: data.get (行 421, high)
    ⚠️  阻塞调用: data.get (行 422, high)
    ⚠️  阻塞调用: data.get (行 427, high)
    ⚠️  阻塞调用: data.get (行 428, high)
    ⚠️  阻塞调用: data.get (行 431, high)
    ⚠️  阻塞调用: data.get (行 432, high)
    ⚠️  阻塞调用: data.get (行 433, high)
    ⚠️  阻塞调用: weather.get (行 434, high)
    ⚠️  阻塞调用: weather.get (行 435, high)
    ⚠️  阻塞调用: rain_data.get (行 436, high)
    ⚠️  阻塞调用: rain_data.get (行 437, high)
    ⚠️  阻塞调用: data.get (行 440, high)
    ⚠️  阻塞调用: data.get (行 441, high)
  - Line 446: `_fetch_openweather_forecast` (await: 2)
    ⚠️  阻塞调用: session.get (行 461, high)
    ⚠️  阻塞调用: data.get (行 470, high)
    ⚠️  阻塞调用: item.get (行 471, high)
    ⚠️  阻塞调用: item.get (行 472, high)
    ⚠️  阻塞调用: item.get (行 474, high)
    ⚠️  阻塞调用: item.get (行 475, high)
    ⚠️  阻塞调用: weather.get (行 476, high)
    ⚠️  阻塞调用: rain_data.get (行 477, high)
    ⚠️  阻塞调用: item.get (行 478, high)
    ⚠️  阻塞调用: data.get (行 484, high)
    ⚠️  阻塞调用: data.get (行 485, high)
  - Line 492: `_fetch_openweather_hourly` (await: 1)
    ⚠️  阻塞调用: _fetch_openweather_forecast (行 495, high)
  - Line 498: `_fetch_openweather_by_coords` (await: 2)
    ⚠️  阻塞调用: session.get (行 513, high)
    ⚠️  阻塞调用: data.get (行 520, high)
    ⚠️  阻塞调用: data.get (行 521, high)
    ⚠️  阻塞调用: data.get (行 528, high)
    ⚠️  阻塞调用: data.get (行 530, high)
    ⚠️  阻塞调用: data.get (行 531, high)
    ⚠️  阻塞调用: weather.get (行 532, high)
    ⚠️  阻塞调用: rain_data.get (行 533, high)
    ⚠️  阻塞调用: rain_data.get (行 534, high)
  - Line 541: `_fetch_qweather_current` (await: 2)
    ⚠️  阻塞调用: session.get (行 558, high)
    ⚠️  阻塞调用: data.get (行 565, high)
    ⚠️  阻塞调用: now.get (行 573, high)
    ⚠️  阻塞调用: now.get (行 574, high)
    ⚠️  阻塞调用: now.get (行 575, high)
    ⚠️  阻塞调用: now.get (行 576, high)
    ⚠️  阻塞调用: now.get (行 577, high)
    ⚠️  阻塞调用: now.get (行 578, high)
    ⚠️  阻塞调用: now.get (行 579, high)
    ⚠️  阻塞调用: now.get (行 580, high)
  - Line 585: `_fetch_qweather_forecast` (await: 2)
    ⚠️  阻塞调用: session.get (行 601, high)
    ⚠️  阻塞调用: data.get (行 608, high)
    ⚠️  阻塞调用: day.get (行 612, high)
    ⚠️  阻塞调用: day.get (行 613, high)
    ⚠️  阻塞调用: day.get (行 614, high)
    ⚠️  阻塞调用: day.get (行 615, high)
    ⚠️  阻塞调用: day.get (行 616, high)
    ⚠️  阻塞调用: day.get (行 617, high)
    ⚠️  阻塞调用: day.get (行 618, high)
    ⚠️  阻塞调用: day.get (行 619, high)
  - Line 632: `_fetch_qweather_hourly` (await: 2)
    ⚠️  阻塞调用: session.get (行 648, high)
    ⚠️  阻塞调用: data.get (行 655, high)
    ⚠️  阻塞调用: hour.get (行 659, high)
    ⚠️  阻塞调用: hour.get (行 660, high)
    ⚠️  阻塞调用: hour.get (行 661, high)
    ⚠️  阻塞调用: hour.get (行 662, high)
    ⚠️  阻塞调用: hour.get (行 663, high)
    ⚠️  阻塞调用: hour.get (行 664, high)
  - Line 677: `_fetch_qweather_by_coords` (await: 2)
    ⚠️  阻塞调用: session.get (行 692, high)
    ⚠️  阻塞调用: data.get (行 699, high)
    ⚠️  阻塞调用: now.get (行 707, high)
    ⚠️  阻塞调用: now.get (行 708, high)
    ⚠️  阻塞调用: now.get (行 709, high)
    ⚠️  阻塞调用: now.get (行 710, high)
    ⚠️  阻塞调用: now.get (行 711, high)
  - Line 716: `_get_qweather_city_id` (await: 1)
    ⚠️  阻塞调用: session.get (行 735, high)
    ⚠️  阻塞调用: data.get (行 740, high)
  - Line 749: `main` (await: 1)
    ⚠️  阻塞调用: platform.system (行 751, high)
    ⚠️  阻塞调用: server.run (行 757, high)

### src\flood_decision_agent\mcp\servers\web_search_server.py
  - Line 59: `list_tools` (无await)
  - Line 165: `call_tool` (await: 5)
    ⚠️  阻塞调用: json.dumps (行 183, low)
  - Line 192: `_handle_web_search` (await: 2)
    ⚠️  阻塞调用: json.dumps (行 198, low)
    ⚠️  阻塞调用: args.get (行 206, high)
    ⚠️  阻塞调用: json.dumps (行 212, low)
    ⚠️  阻塞调用: session.post (行 247, high)
    ⚠️  阻塞调用: message.get (行 270, high)
    ⚠️  阻塞调用: message.get (行 273, high)
    ⚠️  阻塞调用: citation.get (行 282, high)
    ⚠️  阻塞调用: citation.get (行 283, high)
    ⚠️  阻塞调用: citation.get (行 284, high)
    ⚠️  阻塞调用: json.dumps (行 291, low)
    ⚠️  阻塞调用: json.dumps (行 297, low)
  - Line 305: `_handle_fetch_webpage` (await: 2)
    ⚠️  阻塞调用: args.get (行 308, high)
    ⚠️  阻塞调用: json.dumps (行 318, low)
    ⚠️  阻塞调用: json.dumps (行 328, low)
    ⚠️  阻塞调用: json.dumps (行 334, low)
    ⚠️  阻塞调用: session.post (行 371, high)
    ⚠️  阻塞调用: message.get (行 391, high)
    ⚠️  阻塞调用: message.get (行 398, high)
    ⚠️  阻塞调用: json.dumps (行 404, low)
    ⚠️  阻塞调用: json.dumps (行 410, low)
  - Line 418: `_handle_news_search` (await: 1)
    ⚠️  阻塞调用: args.get (行 421, high)
    ⚠️  阻塞调用: args.get (行 422, high)
  - Line 434: `_handle_academic_search` (await: 1)
    ⚠️  阻塞调用: args.get (行 437, high)
  - Line 449: `_handle_check_api_status` (await: 1)
    ⚠️  阻塞调用: session.get (行 466, high)
    ⚠️  阻塞调用: m.get (行 474, high)
    ⚠️  阻塞调用: data.get (行 474, high)
    ⚠️  阻塞调用: json.dumps (行 487, low)
  - Line 491: `main` (await: 1)
    ⚠️  阻塞调用: platform.system (行 493, high)
    ⚠️  阻塞调用: server.run (行 499, high)

### src\flood_decision_agent\mcp\servers\yolo_vision_server.py
  - Line 138: `list_tools` (无await)
  - Line 265: `call_tool` (await: 6)
    ⚠️  阻塞调用: json.dumps (行 287, low)
  - Line 295: `_handle_detect_flood` (无await)
    ⚠️  阻塞调用: args.get (行 303, high)
    ⚠️  阻塞调用: args.get (行 304, high)
    ⚠️  阻塞调用: json.dumps (行 345, low)
  - Line 358: `_handle_detect_water` (无await)
    ⚠️  阻塞调用: args.get (行 366, high)
    ⚠️  阻塞调用: args.get (行 367, high)
    ⚠️  阻塞调用: json.dumps (行 404, low)
  - Line 417: `_handle_detect_infrastructure` (无await)
    ⚠️  阻塞调用: args.get (行 425, high)
    ⚠️  阻塞调用: args.get (行 426, high)
    ⚠️  阻塞调用: json.dumps (行 463, low)
  - Line 476: `_handle_batch_detect` (无await)
    ⚠️  阻塞调用: args.get (行 484, high)
    ⚠️  阻塞调用: args.get (行 485, high)
    ⚠️  阻塞调用: json.dumps (行 500, low)
    ⚠️  阻塞调用: json.dumps (行 546, low)
  - Line 559: `_handle_model_info` (无await)
    ⚠️  阻塞调用: json.dumps (行 565, low)
    ⚠️  阻塞调用: json.dumps (行 596, low)
    ⚠️  阻塞调用: json.dumps (行 612, low)
  - Line 620: `_handle_download_dataset` (无await)
    ⚠️  阻塞调用: json.dumps (行 626, low)
    ⚠️  阻塞调用: args.get (行 634, high)
    ⚠️  阻塞调用: cv2.imwrite (行 665, high)
    ⚠️  阻塞调用: json.dumps (行 670, low)
    ⚠️  阻塞调用: json.dumps (行 683, low)
  - Line 692: `main` (await: 1)
    ⚠️  阻塞调用: platform.system (行 697, high)
    ⚠️  阻塞调用: server.run (行 705, high)

### tests\e2e\test_detailed_websocket.py
  - Line 10: `test_chat_detailed` (await: 3)
    ⚠️  阻塞调用: json.loads (行 18, low)
    ⚠️  阻塞调用: json.dumps (行 23, low)
    ⚠️  阻塞调用: json.loads (行 34, low)
    ⚠️  阻塞调用: data.get (行 37, high)
    ⚠️  阻塞调用: data.get (行 42, high)
    ⚠️  阻塞调用: data.get (行 44, high)
    ⚠️  阻塞调用: data.get (行 44, high)
    ⚠️  阻塞调用: data.get (行 46, high)
    ⚠️  阻塞调用: data.get (行 48, high)
    ⚠️  阻塞调用: data.get (行 50, high)
    ⚠️  阻塞调用: data.get (行 50, high)
    ⚠️  阻塞调用: data.get (行 52, high)
    ⚠️  阻塞调用: data.get (行 52, high)
    ⚠️  阻塞调用: data.get (行 54, high)
    ⚠️  阻塞调用: data.get (行 56, high)
    ⚠️  阻塞调用: data.get (行 59, high)
    ⚠️  阻塞调用: msg.get (行 69, high)

### tests\e2e\test_simple_websocket.py
  - Line 10: `test_chat` (await: 3)
    ⚠️  阻塞调用: json.loads (行 18, low)
    ⚠️  阻塞调用: json.dumps (行 23, low)
    ⚠️  阻塞调用: json.loads (行 33, low)
    ⚠️  阻塞调用: data.get (行 34, high)
    ⚠️  阻塞调用: data.get (行 36, high)
    ⚠️  阻塞调用: data.get (行 37, high)
    ⚠️  阻塞调用: data.get (行 39, high)
    ⚠️  阻塞调用: data.get (行 40, high)

### tests\e2e\test_websocket_e2e.py
  - Line 20: `test_websocket_connection` (await: 1)
    ⚠️  阻塞调用: json.loads (行 26, low)
    ⚠️  阻塞调用: data.get (行 29, high)
  - Line 35: `test_ping_pong` (await: 3)
    ⚠️  阻塞调用: json.dumps (行 43, low)
    ⚠️  阻塞调用: json.loads (行 47, low)
    ⚠️  阻塞调用: data.get (行 50, high)
  - Line 56: `test_chat_message_flow` (await: 3)
    ⚠️  阻塞调用: json.dumps (行 66, low)
    ⚠️  阻塞调用: json.loads (行 78, low)
    ⚠️  阻塞调用: data.get (行 81, high)
    ⚠️  阻塞调用: data.get (行 84, high)
    ⚠️  阻塞调用: m.get (行 91, high)
    ⚠️  阻塞调用: m.get (行 96, high)
  - Line 107: `test_plan_mode_flow` (await: 5)
    ⚠️  阻塞调用: json.dumps (行 118, low)
    ⚠️  阻塞调用: json.loads (行 127, low)
    ⚠️  阻塞调用: data.get (行 130, high)
    ⚠️  阻塞调用: data.get (行 132, high)
    ⚠️  阻塞调用: data.get (行 133, high)
    ⚠️  阻塞调用: data.get (行 136, high)
    ⚠️  阻塞调用: m.get (行 143, high)
    ⚠️  阻塞调用: json.dumps (行 148, low)
    ⚠️  阻塞调用: json.loads (行 159, low)
    ⚠️  阻塞调用: data.get (行 162, high)
    ⚠️  阻塞调用: data.get (行 164, high)
    ⚠️  阻塞调用: m.get (行 170, high)
  - Line 188: `test_message_sequence_integrity` (await: 3)
    ⚠️  阻塞调用: json.dumps (行 198, low)
    ⚠️  阻塞调用: json.loads (行 208, low)
    ⚠️  阻塞调用: data.get (行 211, high)
    ⚠️  阻塞调用: m.get (行 217, high)
  - Line 235: `run_all_tests` (await: 1)

### tests\integration\test_advanced_pipeline.py
  - Line 22: `start_mcp_servers` (await: 1)
  - Line 230: `setup` (await: 1)
  - Line 250: `execute` (await: 2)
    ⚠️  阻塞调用: result.get (行 265, high)
    ⚠️  阻塞调用: result.get (行 267, high)
    ⚠️  阻塞调用: result.get (行 269, high)
  - Line 280: `main` (无await)
    ⚠️  阻塞调用: os.environ.get (行 290, high)

### tests\integration\test_websocket_chain_generation.py
  - Line 31: `accept` (无await)
  - Line 34: `send_json` (无await)
  - Line 37: `send_text` (无await)
  - Line 40: `receive_text` (await: 1)
    ⚠️  阻塞调用: asyncio.sleep (行 42, high)
    ⚠️  阻塞调用: json.dumps (行 43, low)
  - Line 45: `close` (无await)
  - Line 94: `test_visualizer_initialization` (无await)
  - Line 109: `test_visualizer_send_event` (await: 1)
  - Line 134: `test_handler_initialization` (无await)
  - Line 142: `test_empty_message_handling` (await: 1)
  - Line 160: `test_full_chat_flow` (await: 1)
    ⚠️  阻塞调用: m.get (行 177, high)
  - Line 186: `test_missing_plan_id` (await: 1)
  - Line 203: `test_cancel_action` (await: 1)
  - Line 224: `test_full_plan_flow` (await: 1)
    ⚠️  阻塞调用: m.get (行 241, high)
  - Line 249: `test_missing_feature_name` (await: 1)
  - Line 266: `test_cancel_action` (await: 1)
  - Line 290: `test_cancel_operation` (await: 1)
  - Line 441: `test_websocket_visualizer_integration` (await: 1)
    ⚠️  阻塞调用: asyncio.sleep (行 468, high)
    ⚠️  阻塞调用: m.get (行 474, high)
  - Line 479: `test_visualizer_pipeline_start` (await: 1)
    ⚠️  阻塞调用: asyncio.sleep (行 493, high)
    ⚠️  阻塞调用: m.get (行 499, high)
  - Line 508: `test_handler_exception_handling` (await: 1)

### tests\integration\test_websocket_integration.py
  - Line 97: `mock_stream_generate` (await: 2)
    ⚠️  阻塞调用: kwargs.get (行 98, high)
  - Line 149: `mock_stream_generate` (await: 2)
    ⚠️  阻塞调用: kwargs.get (行 150, high)

### tests\mcp\start_all_mcp_servers.py
  - Line 17: `start_and_test_all_servers` (await: 7)
    ⚠️  阻塞调用: result.get (行 68, high)
    ⚠️  阻塞调用: result.get (行 70, high)
    ⚠️  阻塞调用: status.get (行 72, high)
    ⚠️  阻塞调用: result.get (行 75, high)
    ⚠️  阻塞调用: result.get (行 84, high)
    ⚠️  阻塞调用: result.get (行 85, high)
    ⚠️  阻塞调用: result.get (行 87, high)
    ⚠️  阻塞调用: result.get (行 98, high)
    ⚠️  阻塞调用: result.get (行 99, high)
    ⚠️  阻塞调用: result.get (行 102, high)
    ⚠️  阻塞调用: asyncio.sleep (行 123, high)

### tests\mcp\test_all_mcp_servers.py
  - Line 17: `test_all_servers` (await: 9)
    ⚠️  阻塞调用: result.get (行 71, high)
    ⚠️  阻塞调用: result.get (行 72, high)
    ⚠️  阻塞调用: s.get (行 73, high)
    ⚠️  阻塞调用: result.get (行 76, high)
    ⚠️  阻塞调用: result.get (行 85, high)
    ⚠️  阻塞调用: result.get (行 86, high)
    ⚠️  阻塞调用: result.get (行 97, high)
    ⚠️  阻塞调用: result.get (行 98, high)
    ⚠️  阻塞调用: result.get (行 127, high)
    ⚠️  阻塞调用: result.get (行 128, high)

### tests\mcp\test_mcp_auto_select.py
  - Line 25: `test_mcp_initialization` (await: 1)
    ⚠️  阻塞调用: tool_info.get (行 45, high)
  - Line 116: `test_mcp_tool_execution` (await: 1)
    ⚠️  阻塞调用: first_tool_info.get (行 144, high)
    ⚠️  阻塞调用: result.get (行 162, high)
    ⚠️  阻塞调用: result.get (行 164, high)
    ⚠️  阻塞调用: result.get (行 166, high)
  - Line 215: `test_mcp_manager_directly` (await: 2)

### tests\mcp\test_mcp_document.py
  - Line 24: `test_mcp_document_service` (await: 4)
    ⚠️  阻塞调用: result.get (行 66, high)
    ⚠️  阻塞调用: result.get (行 67, high)
    ⚠️  阻塞调用: result.get (行 68, high)
    ⚠️  阻塞调用: result.get (行 70, high)
    ⚠️  阻塞调用: result.get (行 71, high)
    ⚠️  阻塞调用: result.get (行 92, high)
    ⚠️  阻塞调用: result.get (行 94, high)
    ⚠️  阻塞调用: result.get (行 95, high)
    ⚠️  阻塞调用: result.get (行 96, high)
    ⚠️  阻塞调用: result.get (行 97, high)
    ⚠️  阻塞调用: result.get (行 100, high)
    ⚠️  阻塞调用: result.get (行 107, high)
  - Line 118: `test_with_unit_task_agent` (await: 4)
    ⚠️  阻塞调用: result1.get (行 157, high)
    ⚠️  阻塞调用: result2.get (行 168, high)
    ⚠️  阻塞调用: result2.get (行 170, high)
    ⚠️  阻塞调用: result2.get (行 171, high)
    ⚠️  阻塞调用: result2.get (行 172, high)
  - Line 186: `main` (await: 2)

### tests\mcp\test_mcp_executor_integration.py
  - Line 27: `test_mcp_tool_integration` (await: 3)
    ⚠️  阻塞调用: result.get (行 76, high)
    ⚠️  阻塞调用: result.get (行 78, high)
    ⚠️  阻塞调用: result.get (行 80, high)
  - Line 89: `test_executor_with_mcp` (await: 2)
  - Line 141: `test_mcp_tool_via_executor` (await: 3)
    ⚠️  阻塞调用: result.get (行 175, high)
    ⚠️  阻塞调用: result.get (行 177, high)
    ⚠️  阻塞调用: result.get (行 179, high)
  - Line 192: `test_tool_registry_integration` (await: 2)
  - Line 238: `main` (await: 4)

### tests\mcp\test_mcp_full_agent.py
  - Line 40: `initialize` (await: 1)
  - Line 71: `execute_task` (await: 1)
    ⚠️  阻塞调用: result.get (行 83, high)
  - Line 88: `run_full_workflow` (await: 7)
    ⚠️  阻塞调用: result1.get (行 107, high)
    ⚠️  阻塞调用: result1.get (行 108, high)
    ⚠️  阻塞调用: result1.get (行 110, high)
    ⚠️  阻塞调用: result2.get (行 125, high)
    ⚠️  阻塞调用: result2.get (行 126, high)
    ⚠️  阻塞调用: result2.get (行 127, high)
    ⚠️  阻塞调用: result2.get (行 128, high)
    ⚠️  阻塞调用: result2.get (行 130, high)
    ⚠️  阻塞调用: result3.get (行 148, high)
    ⚠️  阻塞调用: result3.get (行 149, high)
    ⚠️  阻塞调用: outputs.get (行 151, high)
    ⚠️  阻塞调用: outputs.get (行 152, high)
    ⚠️  阻塞调用: result3.get (行 157, high)
    ⚠️  阻塞调用: result3.get (行 163, high)
    ⚠️  阻塞调用: result4.get (行 176, high)
    ⚠️  阻塞调用: result4.get (行 177, high)
    ⚠️  阻塞调用: outputs.get (行 179, high)
    ⚠️  阻塞调用: result4.get (行 181, high)
    ⚠️  阻塞调用: result4.get (行 187, high)
    ⚠️  阻塞调用: result5.get (行 207, high)
    ⚠️  阻塞调用: result5.get (行 208, high)
    ⚠️  阻塞调用: plan.get (行 210, high)
    ⚠️  阻塞调用: plan.get (行 211, high)
    ⚠️  阻塞调用: plan.get (行 212, high)
    ⚠️  阻塞调用: result5.get (行 214, high)
    ⚠️  阻塞调用: result3.get (行 230, high)
    ⚠️  阻塞调用: result3.get (行 231, high)
    ⚠️  阻塞调用: result4.get (行 236, high)
    ⚠️  阻塞调用: result5.get (行 241, high)
    ⚠️  阻塞调用: result5.get (行 242, high)
    ⚠️  阻塞调用: result5.get (行 243, high)
    ⚠️  阻塞调用: result6.get (行 266, high)
    ⚠️  阻塞调用: result6.get (行 268, high)
    ⚠️  阻塞调用: result6.get (行 270, high)
    ⚠️  阻塞调用: result7.get (行 280, high)
    ⚠️  阻塞调用: result7.get (行 281, high)
    ⚠️  阻塞调用: plan.get (行 284, high)
    ⚠️  阻塞调用: plan.get (行 284, high)
  - Line 288: `close` (await: 1)
  - Line 295: `test_individual_servers` (await: 12)
    ⚠️  阻塞调用: result.get (行 324, high)
    ⚠️  阻塞调用: result.get (行 332, high)
    ⚠️  阻塞调用: result.get (行 357, high)
    ⚠️  阻塞调用: model.get (行 360, high)
    ⚠️  阻塞调用: model.get (行 360, high)
    ⚠️  阻塞调用: result.get (行 371, high)
    ⚠️  阻塞调用: result.get (行 372, high)
    ⚠️  阻塞调用: outputs.get (行 374, high)
    ⚠️  阻塞调用: result.get (行 376, high)
    ⚠️  阻塞调用: result.get (行 401, high)
    ⚠️  阻塞调用: result.get (行 403, high)
    ⚠️  阻塞调用: result2.get (行 411, high)
    ⚠️  阻塞调用: result2.get (行 413, high)
    ⚠️  阻塞调用: result2.get (行 415, high)
    ⚠️  阻塞调用: result.get (行 417, high)
  - Line 424: `main` (await: 4)
    ⚠️  阻塞调用: r.get (行 449, high)

### tests\mcp\test_mcp_pipeline.py
  - Line 274: `test_mcp_tools_directly` (await: 3)
    ⚠️  阻塞调用: tool.get (行 303, high)
    ⚠️  阻塞调用: tool.get (行 304, high)
    ⚠️  阻塞调用: t.get (行 309, high)
    ⚠️  阻塞调用: tool.get (行 313, high)

### tests\mcp\test_mcp_simple.py
  - Line 12: `test_document_server` (await: 3)
    ⚠️  阻塞调用: result.get (行 60, high)
    ⚠️  阻塞调用: result.get (行 62, high)
    ⚠️  阻塞调用: result.get (行 64, high)
  - Line 74: `test_all_servers` (await: 2)
  - Line 119: `main` (await: 2)

### tests\mcp\test_rainfall_mcp.py
  - Line 17: `test_rainfall_mcp` (await: 7)
    ⚠️  阻塞调用: manager.clients.get (行 33, high)
    ⚠️  阻塞调用: status_result.get (行 45, high)
    ⚠️  阻塞调用: status_result.get (行 49, high)
    ⚠️  阻塞调用: p.get (行 50, high)
    ⚠️  阻塞调用: current_result.get (行 70, high)
    ⚠️  阻塞调用: current_result.get (行 71, high)
    ⚠️  阻塞调用: current_result.get (行 72, high)
    ⚠️  阻塞调用: current_result.get (行 73, high)
    ⚠️  阻塞调用: current.get (行 74, high)
    ⚠️  阻塞调用: current.get (行 75, high)
    ⚠️  阻塞调用: current.get (行 76, high)
    ⚠️  阻塞调用: current.get (行 76, high)
    ⚠️  阻塞调用: forecast_result.get (行 88, high)
    ⚠️  阻塞调用: forecast_result.get (行 89, high)
    ⚠️  阻塞调用: forecast_result.get (行 90, high)
    ⚠️  阻塞调用: f.get (行 93, high)
    ⚠️  阻塞调用: f.get (行 93, high)
    ⚠️  阻塞调用: f.get (行 94, high)
    ⚠️  阻塞调用: f.get (行 94, high)
    ⚠️  阻塞调用: hourly_result.get (行 107, high)
    ⚠️  阻塞调用: hourly_result.get (行 108, high)
    ⚠️  阻塞调用: hourly_result.get (行 109, high)
    ⚠️  阻塞调用: f.get (行 112, high)
    ⚠️  阻塞调用: f.get (行 112, high)
    ⚠️  阻塞调用: f.get (行 113, high)
    ⚠️  阻塞调用: f.get (行 113, high)
    ⚠️  阻塞调用: coords_result.get (行 126, high)
    ⚠️  阻塞调用: coords_result.get (行 127, high)
    ⚠️  阻塞调用: coords_result.get (行 128, high)
    ⚠️  阻塞调用: coords_result.get (行 129, high)
    ⚠️  阻塞调用: coords.get (行 130, high)
    ⚠️  阻塞调用: coords.get (行 130, high)
    ⚠️  阻塞调用: coords_result.get (行 131, high)
    ⚠️  阻塞调用: current.get (行 132, high)

### tests\mcp\test_web_search_server.py
  - Line 41: `test_check_api_status` (await: 1)
    ⚠️  阻塞调用: json.loads (行 48, low)
    ⚠️  阻塞调用: data.get (行 50, high)
    ⚠️  阻塞调用: data.get (行 51, high)
    ⚠️  阻塞调用: data.get (行 53, high)
    ⚠️  阻塞调用: data.get (行 56, high)
    ⚠️  阻塞调用: data.get (行 59, high)
  - Line 62: `test_web_search` (await: 1)
    ⚠️  阻塞调用: json.loads (行 75, low)
    ⚠️  阻塞调用: data.get (行 77, high)
    ⚠️  阻塞调用: data.get (行 79, high)
    ⚠️  阻塞调用: data.get (行 80, high)
    ⚠️  阻塞调用: data.get (行 82, high)
    ⚠️  阻塞调用: data.get (行 88, high)
    ⚠️  阻塞调用: data.get (行 90, high)
  - Line 93: `test_news_search` (await: 1)
    ⚠️  阻塞调用: json.loads (行 106, low)
    ⚠️  阻塞调用: data.get (行 108, high)
    ⚠️  阻塞调用: data.get (行 110, high)
    ⚠️  阻塞调用: data.get (行 112, high)
    ⚠️  阻塞调用: data.get (行 114, high)
  - Line 117: `test_academic_search` (await: 1)
    ⚠️  阻塞调用: json.loads (行 130, low)
    ⚠️  阻塞调用: data.get (行 132, high)
    ⚠️  阻塞调用: data.get (行 134, high)
    ⚠️  阻塞调用: data.get (行 136, high)
    ⚠️  阻塞调用: data.get (行 138, high)
  - Line 141: `test_fetch_webpage` (await: 1)
    ⚠️  阻塞调用: json.loads (行 154, low)
    ⚠️  阻塞调用: data.get (行 156, high)
    ⚠️  阻塞调用: data.get (行 158, high)
    ⚠️  阻塞调用: data.get (行 162, high)
    ⚠️  阻塞调用: data.get (行 164, high)
  - Line 167: `run_all_tests` (await: 5)

### tests\mcp\test_yolo_vision_mcp.py
  - Line 17: `test_yolo_vision_mcp` (await: 8)
    ⚠️  阻塞调用: manager.clients.get (行 33, high)
    ⚠️  阻塞调用: info_result.get (行 45, high)
    ⚠️  阻塞调用: info_result.get (行 46, high)
    ⚠️  阻塞调用: info_result.get (行 49, high)
    ⚠️  阻塞调用: info_result.get (行 56, high)
    ⚠️  阻塞调用: info_result.get (行 57, high)
    ⚠️  阻塞调用: info_result.get (行 58, high)
    ⚠️  阻塞调用: info_result.get (行 59, high)
    ⚠️  阻塞调用: dataset_result.get (行 66, high)
    ⚠️  阻塞调用: dataset_result.get (行 68, high)
    ⚠️  阻塞调用: dataset_result.get (行 72, high)
    ⚠️  阻塞调用: dataset_result.get (行 73, high)
    ⚠️  阻塞调用: flood_result.get (行 86, high)
    ⚠️  阻塞调用: flood_result.get (行 87, high)
    ⚠️  阻塞调用: flood_result.get (行 88, high)
    ⚠️  阻塞调用: water_result.get (行 99, high)
    ⚠️  阻塞调用: water_result.get (行 100, high)
    ⚠️  阻塞调用: infra_result.get (行 111, high)
    ⚠️  阻塞调用: infra_result.get (行 112, high)
    ⚠️  阻塞调用: batch_result.get (行 121, high)
    ⚠️  阻塞调用: batch_result.get (行 122, high)
    ⚠️  阻塞调用: batch_result.get (行 123, high)

### tests\test_websocket_live.py
  - Line 11: `test_websocket` (await: 5)
    ⚠️  阻塞调用: json.loads (行 18, low)
    ⚠️  阻塞调用: json.dumps (行 22, low)
    ⚠️  阻塞调用: json.loads (行 24, low)
    ⚠️  阻塞调用: json.dumps (行 28, low)
    ⚠️  阻塞调用: json.loads (行 38, low)
    ⚠️  阻塞调用: data.get (行 39, high)
    ⚠️  阻塞调用: data.get (行 40, high)

### tests\unit\agents\decision_chain\test_chain_generator.py
  - Line 41: `test_generate_normal_mode` (无await)
  - Line 65: `test_generate_with_intent_error` (无await)
  - Line 86: `test_generate_from_plan` (无await)
  - Line 114: `test_generate_from_plan_empty_steps` (无await)
  - Line 129: `test_generate_from_spec` (无await)
  - Line 176: `test_generate_exception_handling` (无await)

### tests\unit\agents\task_executor\test_streaming_executor.py
  - Line 61: `test_execute_empty_graph` (无await)
  - Line 78: `test_execute_with_tasks` (无await)
  - Line 103: `test_execute_task_failure` (无await)
    ⚠️  阻塞调用: kwargs.get (行 106, high)
  - Line 127: `test_execute_exception_handling` (无await)
  - Line 143: `test_cancel_execution` (无await)
  - Line 185: `test_task_detail_in_events` (无await)
  - Line 209: `test_execution_progress_events` (无await)

### tests\unit\test_websocket_handlers.py
  - Line 44: `test_stream_generate_without_client` (await: 1)
  - Line 68: `test_handle_chat_message` (await: 1)
  - Line 80: `test_handle_known_message` (await: 1)
  - Line 108: `test_handle_start_plan` (await: 1)
  - Line 144: `test_handle_start_spec` (await: 1)
  - Line 172: `test_handle_ping` (await: 1)

### web\backend\api\chain_generation.py
  - Line 99: `generate_chain` (无await)
    ⚠️  阻塞调用: router.post (行 98, high)
  - Line 144: `generate_chain_from_plan` (无await)
    ⚠️  阻塞调用: doc.get (行 163, high)
    ⚠️  阻塞调用: metadata.get (行 164, high)
    ⚠️  阻塞调用: doc.get (行 174, high)
    ⚠️  阻塞调用: router.post (行 143, high)
  - Line 201: `generate_chain_from_spec` (无await)
    ⚠️  阻塞调用: doc.get (行 220, high)
    ⚠️  阻塞调用: metadata.get (行 221, high)
    ⚠️  阻塞调用: doc.get (行 231, high)
    ⚠️  阻塞调用: router.post (行 200, high)
  - Line 258: `get_chain_generation_status` (无await)
    ⚠️  阻塞调用: gen_info.get (行 273, high)
    ⚠️  阻塞调用: gen_info.get (行 274, high)
    ⚠️  阻塞调用: gen_info.get (行 275, high)
    ⚠️  阻塞调用: gen_info.get (行 276, high)
    ⚠️  阻塞调用: router.get (行 257, high)
  - Line 285: `execute_chain` (无await)
    ⚠️  阻塞调用: gen_info.get (行 299, high)
    ⚠️  阻塞调用: router.post (行 284, high)
  - Line 333: `get_chain_execution_status` (无await)
    ⚠️  阻塞调用: exec_info.get (行 347, high)
    ⚠️  阻塞调用: exec_info.get (行 348, high)
    ⚠️  阻塞调用: exec_info.get (行 349, high)
    ⚠️  阻塞调用: exec_info.get (行 350, high)
    ⚠️  阻塞调用: exec_info.get (行 351, high)
    ⚠️  阻塞调用: router.get (行 332, high)
  - Line 360: `cancel_chain_execution` (无await)
    ⚠️  阻塞调用: exec_info.get (行 372, high)
    ⚠️  阻塞调用: router.post (行 359, high)

### web\backend\api\chat.py
  - Line 450: `stream_chat_response` (await: 2)
    ⚠️  阻塞调用: json.dumps (行 483, low)
    ⚠️  阻塞调用: pipeline.run (行 562, high)
    ⚠️  阻塞调用: json.dumps (行 580, low)
    ⚠️  阻塞调用: asyncio.sleep (行 581, high)
    ⚠️  阻塞调用: json.dumps (行 602, low)
    ⚠️  阻塞调用: asyncio.sleep (行 603, high)
    ⚠️  阻塞调用: json.dumps (行 618, low)
    ⚠️  阻塞调用: json.dumps (行 625, low)
  - Line 629: `chat` (无await)
    ⚠️  阻塞调用: json.loads (行 648, low)
    ⚠️  阻塞调用: data.get (行 649, high)
    ⚠️  阻塞调用: data.get (行 650, high)
    ⚠️  阻塞调用: data.get (行 651, high)
    ⚠️  阻塞调用: data.get (行 652, high)
    ⚠️  阻塞调用: data.get (行 653, high)
    ⚠️  阻塞调用: router.post (行 628, high)
  - Line 662: `get_messages` (无await)
    ⚠️  阻塞调用: _messages.get (行 664, high)
    ⚠️  阻塞调用: router.get (行 661, high)
  - Line 676: `get_process_events` (无await)
    ⚠️  阻塞调用: _process_events.get (行 678, high)
    ⚠️  阻塞调用: router.get (行 675, high)
  - Line 690: `clear_messages` (无await)
    ⚠️  阻塞调用: router.post (行 689, high)

### web\backend\api\conversations.py
  - Line 56: `list_conversations` (无await)
    ⚠️  阻塞调用: router.get (行 55, high)
  - Line 80: `create_conversation` (无await)
    ⚠️  阻塞调用: router.post (行 79, high)
  - Line 112: `get_conversation` (无await)
    ⚠️  阻塞调用: _conversations.get (行 124, high)
    ⚠️  阻塞调用: router.get (行 111, high)
  - Line 138: `delete_conversation` (无await)
  - Line 228: `get_conversation_plans` (无await)
    ⚠️  阻塞调用: plan.get (行 261, high)
    ⚠️  阻塞调用: metadata.get (行 264, high)
    ⚠️  阻塞调用: metadata.get (行 265, high)
    ⚠️  阻塞调用: metadata.get (行 266, high)
    ⚠️  阻塞调用: metadata.get (行 267, high)
    ⚠️  阻塞调用: metadata.get (行 268, high)
    ⚠️  阻塞调用: router.get (行 227, high)
  - Line 293: `get_conversation_specs` (无await)
    ⚠️  阻塞调用: spec.get (行 326, high)
    ⚠️  阻塞调用: metadata.get (行 329, high)
    ⚠️  阻塞调用: metadata.get (行 330, high)
    ⚠️  阻塞调用: metadata.get (行 331, high)
    ⚠️  阻塞调用: metadata.get (行 332, high)
    ⚠️  阻塞调用: metadata.get (行 333, high)
    ⚠️  阻塞调用: metadata.get (行 334, high)
    ⚠️  阻塞调用: router.get (行 292, high)

### web\backend\api\data_acquisition.py
  - Line 163: `parse_input` (无await)
    ⚠️  阻塞调用: schema_map.get (行 181, high)
    ⚠️  阻塞调用: router.post (行 162, high)
  - Line 202: `confirm_data` (无await)
    ⚠️  阻塞调用: router.post (行 201, high)
  - Line 231: `request_data` (无await)
    ⚠️  阻塞调用: router.post (行 230, high)
  - Line 275: `get_default_values` (无await)
    ⚠️  阻塞调用: json.loads (行 286, low)
    ⚠️  阻塞调用: router.get (行 274, high)
  - Line 307: `get_data_lineage` (无await)
    ⚠️  阻塞调用: lineage.get (行 321, high)
    ⚠️  阻塞调用: router.get (行 306, high)
  - Line 336: `create_clarification_session` (无await)
    ⚠️  阻塞调用: router.post (行 335, high)
  - Line 367: `resolve_clarification` (无await)
    ⚠️  阻塞调用: clarification_manager.skip_request (行 392, high)
    ⚠️  阻塞调用: router.post (行 366, high)
  - Line 412: `upload_file` (await: 1)
    ⚠️  阻塞调用: file.read (行 422, high)
    ⚠️  阻塞调用: pd.read_csv (行 428, high)
    ⚠️  阻塞调用: pd.read_excel (行 433, high)
    ⚠️  阻塞调用: router.post (行 411, high)

### web\backend\api\mode.py
  - Line 125: `detect_mode` (无await)
    ⚠️  阻塞调用: router.post (行 124, high)

### web\backend\api\plans.py
  - Line 75: `update_plan` (无await)
    ⚠️  阻塞调用: existing.get (行 91, high)
  - Line 115: `generate_plan` (无await)
    ⚠️  阻塞调用: existing.get (行 142, high)
    ⚠️  阻塞调用: existing.get (行 147, high)
    ⚠️  阻塞调用: router.post (行 114, high)
  - Line 167: `modify_plan` (无await)
    ⚠️  阻塞调用: existing.get (行 187, high)
    ⚠️  阻塞调用: existing.get (行 194, high)
    ⚠️  阻塞调用: router.post (行 166, high)
  - Line 215: `confirm_plan` (无await)
    ⚠️  阻塞调用: existing.get (行 232, high)
    ⚠️  阻塞调用: existing.get (行 238, high)
    ⚠️  阻塞调用: router.post (行 214, high)
  - Line 260: `cancel_plan` (无await)
    ⚠️  阻塞调用: existing.get (行 276, high)
    ⚠️  阻塞调用: existing.get (行 282, high)
    ⚠️  阻塞调用: router.post (行 259, high)

### web\backend\api\sessions.py
  - Line 157: `create_session` (无await)
    ⚠️  阻塞调用: router.post (行 156, high)
  - Line 181: `get_session_status` (无await)
    ⚠️  阻塞调用: router.get (行 180, high)
  - Line 206: `resume_session` (无await)
    ⚠️  阻塞调用: router.post (行 205, high)
  - Line 238: `update_session_state` (无await)
    ⚠️  阻塞调用: router.post (行 237, high)
  - Line 278: `delete_session` (无await)
  - Line 292: `list_sessions` (无await)
    ⚠️  阻塞调用: router.get (行 291, high)
  - Line 328: `resume_session_legacy` (await: 1)
    ⚠️  阻塞调用: router.post (行 327, high)

### web\backend\api\specs.py
  - Line 70: `update_spec` (无await)
    ⚠️  阻塞调用: existing.get (行 86, high)
  - Line 110: `generate_spec` (无await)
    ⚠️  阻塞调用: existing.get (行 137, high)
    ⚠️  阻塞调用: existing.get (行 142, high)
    ⚠️  阻塞调用: router.post (行 109, high)
  - Line 162: `modify_spec` (无await)
    ⚠️  阻塞调用: existing.get (行 182, high)
    ⚠️  阻塞调用: existing.get (行 189, high)
    ⚠️  阻塞调用: router.post (行 161, high)
  - Line 210: `confirm_spec` (无await)
    ⚠️  阻塞调用: existing.get (行 227, high)
    ⚠️  阻塞调用: existing.get (行 233, high)
    ⚠️  阻塞调用: router.post (行 209, high)
  - Line 255: `cancel_spec` (无await)
    ⚠️  阻塞调用: existing.get (行 271, high)
    ⚠️  阻塞调用: existing.get (行 277, high)
    ⚠️  阻塞调用: router.post (行 254, high)
  - Line 313: `list_specs` (无await)
    ⚠️  阻塞调用: doc.get (行 324, high)
    ⚠️  阻塞调用: metadata.get (行 327, high)
    ⚠️  阻塞调用: metadata.get (行 328, high)
    ⚠️  阻塞调用: doc.get (行 329, high)
    ⚠️  阻塞调用: doc.get (行 330, high)
    ⚠️  阻塞调用: router.get (行 312, high)
  - Line 339: `get_spec` (无await)
    ⚠️  阻塞调用: doc.get (行 351, high)
    ⚠️  阻塞调用: doc.get (行 354, high)
    ⚠️  阻塞调用: metadata.get (行 360, high)
    ⚠️  阻塞调用: metadata.get (行 361, high)
    ⚠️  阻塞调用: doc.get (行 365, high)
    ⚠️  阻塞调用: doc.get (行 366, high)
    ⚠️  阻塞调用: router.get (行 338, high)
  - Line 375: `get_spec_files` (无await)
    ⚠️  阻塞调用: doc.get (行 388, high)
    ⚠️  阻塞调用: info.get (行 397, high)
    ⚠️  阻塞调用: info.get (行 398, high)
    ⚠️  阻塞调用: router.get (行 374, high)
  - Line 410: `get_spec_file` (无await)
    ⚠️  阻塞调用: doc.get (行 423, high)
    ⚠️  阻塞调用: doc.get (行 424, high)
    ⚠️  阻塞调用: file_mapping.get (行 439, high)
    ⚠️  阻塞调用: file_info.get (行 450, high)
    ⚠️  阻塞调用: file_info.get (行 452, high)
    ⚠️  阻塞调用: file_info.get (行 453, high)
    ⚠️  阻塞调用: router.get (行 409, high)
  - Line 463: `create_spec` (无await)
    ⚠️  阻塞调用: router.post (行 462, high)
  - Line 493: `update_spec_file` (无await)
    ⚠️  阻塞调用: existing.get (行 507, high)
  - Line 530: `update_spec_section` (无await)
    ⚠️  阻塞调用: existing.get (行 549, high)
    ⚠️  阻塞调用: existing.get (行 553, high)
  - Line 575: `approve_spec` (await: 1)
    ⚠️  阻塞调用: router.post (行 574, high)

### web\backend\main.py
  - Line 41: `lifespan` (无await)
  - Line 70: `health_check` (无await)
    ⚠️  阻塞调用: app.get (行 69, high)

### web\backend\websocket\chat_ws.py
  - Line 32: `connect` (await: 3)
  - Line 76: `send_message` (await: 1)
  - Line 97: `broadcast` (await: 1)
  - Line 120: `websocket_endpoint` (await: 6)
    ⚠️  阻塞调用: json.loads (行 136, low)
    ⚠️  阻塞调用: message.get (行 137, high)

### web\backend\websocket\message_handlers.py
  - Line 50: `handle` (无await)
  - Line 54: `send_message` (await: 1)
    ⚠️  阻塞调用: data.get (行 56, high)
  - Line 63: `handle` (await: 1)
  - Line 95: `handle` (await: 17)
    ⚠️  阻塞调用: message.get (行 97, high)
    ⚠️  阻塞调用: generation_metadata.get (行 216, high)
  - Line 386: `handle` (await: 17)
    ⚠️  阻塞调用: message.get (行 388, high)
    ⚠️  阻塞调用: message.get (行 389, high)
    ⚠️  阻塞调用: doc.get (行 439, high)
    ⚠️  阻塞调用: doc.get (行 440, high)
    ⚠️  阻塞调用: generation_metadata.get (行 511, high)
  - Line 670: `handle` (await: 17)
    ⚠️  阻塞调用: message.get (行 672, high)
    ⚠️  阻塞调用: message.get (行 673, high)
    ⚠️  阻塞调用: doc.get (行 723, high)
    ⚠️  阻塞调用: doc.get (行 724, high)
    ⚠️  阻塞调用: generation_metadata.get (行 795, high)
  - Line 935: `handle` (await: 1)
    ⚠️  阻塞调用: message.get (行 937, high)
    ⚠️  阻塞调用: message.get (行 938, high)
    ⚠️  阻塞调用: message.get (行 939, high)
  - Line 968: `handle` (await: 6)
    ⚠️  阻塞调用: message.get (行 970, high)
    ⚠️  阻塞调用: message.get (行 971, high)
    ⚠️  阻塞调用: asyncio.sleep (行 1042, high)
  - Line 1096: `handle` (await: 6)
    ⚠️  阻塞调用: message.get (行 1098, high)
    ⚠️  阻塞调用: message.get (行 1099, high)
    ⚠️  阻塞调用: asyncio.sleep (行 1189, high)

## 潜在阻塞调用详情

### HIGH 级别
- **uvicorn.run**
  - 位置: start_backend.py:15
  - 代码: `uvicorn.run(app, host='0.0.0.0', port=port)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: debug\demo_fixed.py:18
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: debug\fix_environment.py:21
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: debug\fix_environment.py:258
  - 代码: `open(script_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: debug\fix_environment.py:259
  - 代码: `f.write(script_content)`
  - 建议: 使用异步写入方法

- **config_path.read_text**
  - 位置: debug\run_debug.py:23
  - 代码: `config_path.read_text(encoding='utf-8')`
  - 建议: 使用异步读取方法

- **config.get**
  - 位置: debug\run_debug.py:27
  - 代码: `config.get('seed', 42)`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: debug\test_unit_task_executor_interactive.py:23
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: debug\test_unit_task_executor_interactive.py:78
  - 代码: `config.get('location', '北江')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: debug\test_unit_task_executor_interactive.py:98
  - 代码: `data_pool.get('rainfall_forecast', {})`
  - 建议: 使用 aiohttp

- **rainfall.get**
  - 位置: debug\test_unit_task_executor_interactive.py:99
  - 代码: `rainfall.get('24h', 0)`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: debug\test_unit_task_executor_interactive.py:270
  - 代码: `data_pool.get('inflow_forecast', {})`
  - 建议: 使用 aiohttp

- **inflow.get**
  - 位置: debug\test_unit_task_executor_interactive.py:271
  - 代码: `inflow.get('peak_flow', 1000)`
  - 建议: 使用 aiohttp

- **info.get**
  - 位置: debug\test_unit_task_executor_interactive.py:346
  - 代码: `info.get('task_types', [])`
  - 建议: 使用 aiohttp

- **self._check_blocking_call**
  - 位置: diagnosis\async_analyzer.py:110
  - 代码: `self._check_blocking_call(node, call_name)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **self._is_likely_sync_call**
  - 位置: diagnosis\async_analyzer.py:115
  - 代码: `self._is_likely_sync_call(call_name)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **open**
  - 位置: diagnosis\async_analyzer.py:194
  - 代码: `open(file_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: diagnosis\async_analyzer.py:195
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: diagnosis\async_analyzer.py:313
  - 代码: `open(report_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: diagnosis\async_analyzer.py:314
  - 代码: `f.write(report)`
  - 建议: 使用异步写入方法

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:93
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:142
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:165
  - 代码: `data.get('message', 'Unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:210
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:240
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:258
  - 代码: `data.get('message', 'Unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:291
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:310
  - 代码: `data.get('message', 'Unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\e2e_diagnosis.py:364
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: diagnosis\e2e_diagnosis.py:410
  - 代码: `asyncio.sleep(2)`
  - 建议: 使用 asyncio.sleep

- **asyncio.sleep**
  - 位置: diagnosis\e2e_diagnosis.py:417
  - 代码: `asyncio.sleep(2)`
  - 建议: 使用 asyncio.sleep

- **open**
  - 位置: diagnosis\e2e_diagnosis.py:540
  - 代码: `open(report_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: diagnosis\e2e_diagnosis.py:541
  - 代码: `f.write(report)`
  - 建议: 使用异步写入方法

- **asyncio.run**
  - 位置: diagnosis\e2e_diagnosis.py:550
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.sleep**
  - 位置: diagnosis\performance_tester.py:80
  - 代码: `asyncio.sleep(0.1)`
  - 建议: 使用 asyncio.sleep

- **init_data.get**
  - 位置: diagnosis\performance_tester.py:112
  - 代码: `init_data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\performance_tester.py:174
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: diagnosis\performance_tester.py:245
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **result.details.get**
  - 位置: diagnosis\performance_tester.py:302
  - 代码: `result.details.get('avg_latency_ms', 0)`
  - 建议: 使用 aiohttp

- **result.details.get**
  - 位置: diagnosis\performance_tester.py:309
  - 代码: `result.details.get('avg_roundtrip_ms', 0)`
  - 建议: 使用 aiohttp

- **result.details.get**
  - 位置: diagnosis\performance_tester.py:316
  - 代码: `result.details.get('success_rate', 0)`
  - 建议: 使用 aiohttp

- **result.details.get**
  - 位置: diagnosis\performance_tester.py:323
  - 代码: `result.details.get('success_rate', 0)`
  - 建议: 使用 aiohttp

- **result.details.get**
  - 位置: diagnosis\performance_tester.py:330
  - 代码: `result.details.get('total_duration_ms', 0)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: diagnosis\performance_tester.py:419
  - 代码: `open(report_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: diagnosis\performance_tester.py:420
  - 代码: `f.write(report)`
  - 建议: 使用异步写入方法

- **asyncio.run**
  - 位置: diagnosis\performance_tester.py:429
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **subprocess.run**
  - 位置: diagnosis\run_diagnosis.py:37
  - 代码: `subprocess.run([sys.executable, 'diagnosis/async_analyzer.py'], cwd=os.path.dirname(os.path.dirname(__file__)), capture_output=True, text=True, timeout=120)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: diagnosis\run_diagnosis.py:75
  - 代码: `asyncio.run(test_connection())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: diagnosis\run_diagnosis.py:92
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: diagnosis\run_diagnosis.py:98
  - 代码: `open(env_path, 'r')`
  - 建议: 使用 aiofiles 替代

- **subprocess.Popen**
  - 位置: diagnosis\run_diagnosis.py:107
  - 代码: `subprocess.Popen([sys.executable, '-m', 'web.backend.main'], cwd=os.path.dirname(os.path.dirname(__file__)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=os.environ.copy())`
  - 建议: 使用 aiofiles 替代

- **time.sleep**
  - 位置: diagnosis\run_diagnosis.py:118
  - 代码: `time.sleep(5)`
  - 建议: 使用 asyncio.sleep

- **subprocess.run**
  - 位置: diagnosis\run_diagnosis.py:141
  - 代码: `subprocess.run([sys.executable, 'diagnosis/performance_tester.py'], cwd=os.path.dirname(os.path.dirname(__file__)), capture_output=True, text=True, timeout=300)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **subprocess.run**
  - 位置: diagnosis\run_diagnosis.py:171
  - 代码: `subprocess.run([sys.executable, 'diagnosis/e2e_diagnosis.py'], cwd=os.path.dirname(os.path.dirname(__file__)), capture_output=True, text=True, timeout=300)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **open**
  - 位置: diagnosis\run_diagnosis.py:225
  - 代码: `open(report_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: diagnosis\run_diagnosis.py:226
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: diagnosis\run_diagnosis.py:259
  - 代码: `open(report_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: diagnosis\run_diagnosis.py:260
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: diagnosis\run_diagnosis.py:284
  - 代码: `open(comprehensive_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: diagnosis\run_diagnosis.py:285
  - 代码: `f.write('\n'.join(comprehensive_report))`
  - 建议: 使用异步写入方法

- **time.sleep**
  - 位置: diagnosis\run_diagnosis.py:316
  - 代码: `time.sleep(3)`
  - 建议: 使用 asyncio.sleep

- **open**
  - 位置: evaluation\run_evaluation.py:178
  - 代码: `open(path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **report.get**
  - 位置: evaluation\run_evaluation.py:190
  - 代码: `report.get('created_at', '-')`
  - 建议: 使用 aiohttp

- **report.get**
  - 位置: evaluation\run_evaluation.py:191
  - 代码: `report.get('overall_score', 0)`
  - 建议: 使用 aiohttp

- **report.get**
  - 位置: evaluation\run_evaluation.py:192
  - 代码: `report.get('summary', {})`
  - 建议: 使用 aiohttp

- **report.get**
  - 位置: evaluation\run_evaluation.py:193
  - 代码: `report.get('dimension_scores', {})`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:197
  - 代码: `dimensions.get('effectiveness', 0)`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:198
  - 代码: `dimensions.get('efficiency', 0)`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:199
  - 代码: `dimensions.get('robustness', 0)`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:200
  - 代码: `dimensions.get('safety', 0)`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:201
  - 代码: `dimensions.get('autonomy', 0)`
  - 建议: 使用 aiohttp

- **dimensions.get**
  - 位置: evaluation\run_evaluation.py:202
  - 代码: `dimensions.get('explainability', 0)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: evaluation\run_evaluation.py:209
  - 代码: `open(output_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: evaluation\run_evaluation.py:210
  - 代码: `f.write('\n'.join(lines))`
  - 建议: 使用异步写入方法

- **alt.metadata.get**
  - 位置: examples\demo_decision_chain_generator.py:390
  - 代码: `alt.metadata.get('issues')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: examples\demo_node_scheduler.py:16
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_node_scheduler.py:44
  - 代码: `config.get('location', '北江流域')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_node_scheduler.py:65
  - 代码: `data_pool.get('rainfall_data', {})`
  - 建议: 使用 aiohttp

- **rainfall.get**
  - 位置: examples\demo_node_scheduler.py:66
  - 代码: `rainfall.get('24h_rainfall', 0)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_node_scheduler.py:69
  - 代码: `config.get('catchment_area', 5000)`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_node_scheduler.py:93
  - 代码: `data_pool.get('inflow_forecast', {})`
  - 建议: 使用 aiohttp

- **inflow.get**
  - 位置: examples\demo_node_scheduler.py:94
  - 代码: `inflow.get('peak_flow', 0)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_node_scheduler.py:96
  - 代码: `config.get('reservoir', '飞来峡')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_node_scheduler.py:97
  - 代码: `config.get('limit_flow', 19000)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_node_scheduler.py:152
  - 代码: `config.get('message', '执行完成')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_node_scheduler.py:227
  - 代码: `data_pool.get(key)`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_node_scheduler.py:298
  - 代码: `data_pool.get(key)`
  - 建议: 使用 aiohttp

- **node_result.get**
  - 位置: examples\demo_node_scheduler.py:396
  - 代码: `node_result.get('status', 'unknown')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_node_scheduler.py:407
  - 代码: `data_pool.get(key)`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: examples\demo_unit_task_executor.py:7
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: examples\demo_unit_task_executor.py:28
  - 代码: `config.get('location', '北江流域')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: examples\demo_unit_task_executor.py:44
  - 代码: `data_pool.get('rainfall_forecast', {})`
  - 建议: 使用 aiohttp

- **rainfall.get**
  - 位置: examples\demo_unit_task_executor.py:45
  - 代码: `rainfall.get('next_24h', 0)`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: examples\heuristic_optimizer_demo.py:182
  - 代码: `node.metadata.get('critical_path')`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: examples\heuristic_optimizer_demo.py:183
  - 代码: `node.metadata.get('priority')`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: examples\heuristic_optimizer_demo.py:183
  - 代码: `node.metadata.get('retry_enabled')`
  - 建议: 使用 aiohttp

- **alt.metadata.get**
  - 位置: examples\heuristic_optimizer_demo.py:205
  - 代码: `alt.metadata.get('description', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: examples\interactive_chat.py:113
  - 代码: `result.get('conversation_id')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: examples\interactive_chat.py:116
  - 代码: `result.get('is_new_conversation')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: examples\interactive_chat.py:119
  - 代码: `result.get('flow_action', 'unknown')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: examples\quick_start.py:33
  - 代码: `snapshot.get('rainfall_forecast')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: examples\quick_start.py:34
  - 代码: `snapshot.get('inflow_forecast')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: examples\quick_start.py:35
  - 代码: `snapshot.get('dispatch_plan')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: examples\quick_start.py:36
  - 代码: `snapshot.get('dispatch_order_text')`
  - 建议: 使用 aiohttp

- **os.system**
  - 位置: scripts\stop_web.py:17
  - 代码: `os.system(f'taskkill /F /PID {pid} 2>nul')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.system**
  - 位置: scripts\stop_web.py:20
  - 代码: `os.system(f'kill -TERM {pid} 2>/dev/null')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.system**
  - 位置: scripts\stop_web.py:44
  - 代码: `os.system(f"""for /f "tokens=5" %a in ('netstat -ano ^| findstr :{port} ^| findstr LISTENING') do taskkill /F /PID %a 2>nul""")`
  - 建议: 使用 asyncio.create_subprocess_exec

- **open**
  - 位置: scripts\stop_web.py:50
  - 代码: `open(pid_file, 'r')`
  - 建议: 使用 aiofiles 替代

- **pid_info.get**
  - 位置: scripts\stop_web.py:53
  - 代码: `pid_info.get('backend_pid')`
  - 建议: 使用 aiohttp

- **pid_info.get**
  - 位置: scripts\stop_web.py:54
  - 代码: `pid_info.get('frontend_pid')`
  - 建议: 使用 aiohttp

- **pid_info.get**
  - 位置: scripts\stop_web.py:55
  - 代码: `pid_info.get('backend_port')`
  - 建议: 使用 aiohttp

- **pid_info.get**
  - 位置: scripts\stop_web.py:56
  - 代码: `pid_info.get('frontend_port')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:67
  - 代码: `payload.get('task_request', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:68
  - 代码: `payload.get('execution_summary', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:69
  - 代码: `payload.get('data_pool_snapshot', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:70
  - 代码: `payload.get('task_graph', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:71
  - 代码: `payload.get('node_results', [])`
  - 建议: 使用 aiohttp

- **execution_info.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:177
  - 代码: `execution_info.get('task_request', {})`
  - 建议: 使用 aiohttp

- **execution_info.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:178
  - 代码: `execution_info.get('execution_summary', {})`
  - 建议: 使用 aiohttp

- **execution_info.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:179
  - 代码: `execution_info.get('data_pool_snapshot', {})`
  - 建议: 使用 aiohttp

- **execution_info.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:180
  - 代码: `execution_info.get('node_results', [])`
  - 建议: 使用 aiohttp

- **task_request.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:183
  - 代码: `task_request.get('input', '未知任务')`
  - 建议: 使用 aiohttp

- **task_request.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:184
  - 代码: `task_request.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:187
  - 代码: `execution_summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:188
  - 代码: `execution_summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:189
  - 代码: `execution_summary.get('failed_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:190
  - 代码: `execution_summary.get('total_duration_ms', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:195
  - 代码: `result.get('node_id', 'unknown')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:196
  - 代码: `result.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:197
  - 代码: `result.get('status', 'unknown')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:198
  - 代码: `result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:199
  - 代码: `metrics.get('elapsed_time_ms', 0)`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:200
  - 代码: `metrics.get('tools_used', [])`
  - 建议: 使用 aiohttp

- **execution_info.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:244
  - 代码: `execution_info.get('execution_summary', {})`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:245
  - 代码: `execution_summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:246
  - 代码: `execution_summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: src\flood_decision_agent\agents\summarizer.py:247
  - 代码: `execution_summary.get('total_duration_ms', 0)`
  - 建议: 使用 aiohttp

- **current_state.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\cancel_handler.py:188
  - 代码: `current_state.get('mode', 'unknown')`
  - 建议: 使用 aiohttp

- **self.MODE_TRANSITIONS.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\cancel_handler.py:236
  - 代码: `self.MODE_TRANSITIONS.get(transition_key, 'unknown_transition')`
  - 建议: 使用 aiohttp

- **self._session_states.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\cancel_handler.py:356
  - 代码: `self._session_states.get(session_id)`
  - 建议: 使用 aiohttp

- **self._session_states.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\cancel_handler.py:367
  - 代码: `self._session_states.get(session_id)`
  - 建议: 使用 aiohttp

- **self._session_states.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\cancel_handler.py:381
  - 代码: `self._session_states.get(session_id)`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_generator.py:209
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **graph.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:300
  - 代码: `graph.get(node_id, set())`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:347
  - 代码: `node.metadata.get('required_tools', [])`
  - 建议: 使用 aiohttp

- **node_output_map.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:383
  - 代码: `node_output_map.get(dep_id, set())`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:387
  - 代码: `node.metadata.get('external_input', False)`
  - 建议: 使用 aiohttp

- **dependency_count.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:414
  - 代码: `dependency_count.get(dep, 0)`
  - 建议: 使用 aiohttp

- **dependency_count.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\chain_optimizer.py:417
  - 代码: `dependency_count.get(node.task_id, 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:88
  - 代码: `data.get('state', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:89
  - 代码: `data.get('status', 'active')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:91
  - 代码: `data.get('interruption_reason')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:93
  - 代码: `data.get('created_at', time.time())`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:94
  - 代码: `data.get('updated_at', time.time())`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:95
  - 代码: `data.get('expires_at')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:96
  - 代码: `data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **self._checkpoints.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:139
  - 代码: `self._checkpoints.get(session_id)`
  - 建议: 使用 aiohttp

- **reason_map.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:447
  - 代码: `reason_map.get(reason.lower())`
  - 建议: 使用 aiohttp

- **state.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:465
  - 代码: `state.get('_required_fields', [])`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:482
  - 代码: `payload.get('command')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:488
  - 代码: `payload.get('interruption_reason')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:489
  - 代码: `payload.get('metadata')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:496
  - 代码: `payload.get('validate_state', True)`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:501
  - 代码: `payload.get('status')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:502
  - 代码: `payload.get('reason')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\checkpoint_agent.py:512
  - 代码: `payload.get('error_message')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:163
  - 代码: `tool.get('name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:207
  - 代码: `context.get('description', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:207
  - 代码: `context.get('user_input', '')`
  - 建议: 使用 aiohttp

- **task_tool_mapping.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:210
  - 代码: `task_tool_mapping.get(task_type, [task_type.value.lower()])`
  - 建议: 使用 aiohttp

- **tool_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:235
  - 代码: `tool_info.get('description', '')`
  - 建议: 使用 aiohttp

- **concurrent.futures.ThreadPoolExecutor**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:276
  - 代码: `concurrent.futures.ThreadPoolExecutor()`
  - 建议: 使用异步读取方法

- **asyncio.run**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:281
  - 代码: `asyncio.run(self.initialize_mcp())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **message.payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:286
  - 代码: `message.payload.get('input', '')`
  - 建议: 使用 aiohttp

- **message.payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:287
  - 代码: `message.payload.get('input_type', 'natural_language')`
  - 建议: 使用 aiohttp

- **message.payload.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:288
  - 代码: `message.payload.get('session_id')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:351
  - 代码: `metadata.get('current_phase', 'unknown')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:352
  - 代码: `metadata.get('partial_result', {})`
  - 建议: 使用 aiohttp

- **state.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:436
  - 代码: `state.get('user_input', '')`
  - 建议: 使用 aiohttp

- **state.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:437
  - 代码: `state.get('input_type', 'natural_language')`
  - 建议: 使用 aiohttp

- **checkpoint_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:440
  - 代码: `checkpoint_data.get('interruption_reason')`
  - 建议: 使用 aiohttp

- **checkpoint_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:447
  - 代码: `checkpoint_data.get('interruption_reason')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:581
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:695
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:754
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:814
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:866
  - 代码: `intent.goal.get('description', intent.raw_input or '简单任务')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1024
  - 代码: `intent.goal.get('description', '')`
  - 建议: 使用 aiohttp

- **step.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1361
  - 代码: `step.get('deliverables', '')`
  - 建议: 使用 aiohttp

- **step.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1362
  - 代码: `step.get('responsible', '')`
  - 建议: 使用 aiohttp

- **chain_metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1468
  - 代码: `chain_metadata.get('reliability_score', 0)`
  - 建议: 使用 aiohttp

- **tasks_result.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1897
  - 代码: `tasks_result.get('tasks_document')`
  - 建议: 使用 aiohttp

- **checklist_result.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:1898
  - 代码: `checklist_result.get('checklist_document')`
  - 建议: 使用 aiohttp

- **nodes_by_type.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:232
  - 代码: `nodes_by_type.get(TaskType.DATA_COLLECTION, [])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:358
  - 代码: `data.get('strategy', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:359
  - 代码: `data.get('nodes', [])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:406
  - 代码: `data.get('reason', '')`
  - 建议: 使用 aiohttp

- **node_map.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:573
  - 代码: `node_map.get(current)`
  - 建议: 使用 aiohttp

- **node_map.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:604
  - 代码: `node_map.get(node_id)`
  - 建议: 使用 aiohttp

- **node_map.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\heuristic_optimizer.py:642
  - 代码: `node_map.get(current)`
  - 建议: 使用 aiohttp

- **self._rules.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_decomposer.py:230
  - 代码: `self._rules.get(task_type)`
  - 建议: 使用 aiohttp

- **sub_task_def.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_decomposer.py:324
  - 代码: `sub_task_def.get('inputs', [])`
  - 建议: 使用 aiohttp

- **sub_task_def.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_decomposer.py:333
  - 代码: `sub_task_def.get('description', '')`
  - 建议: 使用 aiohttp

- **sub_task_def.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_decomposer.py:334
  - 代码: `sub_task_def.get('inputs', [])`
  - 建议: 使用 aiohttp

- **sub_task_def.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_decomposer.py:335
  - 代码: `sub_task_def.get('outputs', [])`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:346
  - 代码: `task_data.get('任务名称', task_data.get('名称', '未命名任务'))`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:346
  - 代码: `task_data.get('名称', '未命名任务')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:347
  - 代码: `task_data.get('描述', task_data.get('说明', ''))`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:347
  - 代码: `task_data.get('说明', '')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:349
  - 代码: `task_data.get('任务名称', '')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:350
  - 代码: `task_data.get('描述', '')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:352
  - 代码: `task_data.get('交付物', '')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\task_extractor.py:353
  - 代码: `task_data.get('负责人', '')`
  - 建议: 使用 aiohttp

- **self.STRATEGIES.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:81
  - 代码: `self.STRATEGIES.get(strategy, self.STRATEGIES['plan'])`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:82
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **chain_root.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:212
  - 代码: `chain_root.get('primary', {})`
  - 建议: 使用 aiohttp

- **primary_section.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:214
  - 代码: `primary_section.get('tasks', [])`
  - 建议: 使用 aiohttp

- **chain_root.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:216
  - 代码: `chain_root.get('tasks', [])`
  - 建议: 使用 aiohttp

- **chain_root.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:224
  - 代码: `chain_root.get('alternatives', [])`
  - 建议: 使用 aiohttp

- **alt_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:230
  - 代码: `alt_data.get('tasks', [])`
  - 建议: 使用 aiohttp

- **alt_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:232
  - 代码: `alt_data.get('name', 'unknown')`
  - 建议: 使用 aiohttp

- **alt_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:233
  - 代码: `alt_data.get('strategy', 'default')`
  - 建议: 使用 aiohttp

- **best_alt.optimization_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:268
  - 代码: `best_alt.optimization_info.get('issues', [])`
  - 建议: 使用 aiohttp

- **best_alt.optimization_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:340
  - 代码: `best_alt.optimization_info.get('issues', [])`
  - 建议: 使用 aiohttp

- **alt.optimization_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:368
  - 代码: `alt.optimization_info.get('issues', [])`
  - 建议: 使用 aiohttp

- **optimized_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:393
  - 代码: `optimized_data.get('tasks', [])`
  - 建议: 使用 aiohttp

- **optimized_data.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:404
  - 代码: `optimized_data.get('optimization', {})`
  - 建议: 使用 aiohttp

- **opt_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:406
  - 代码: `opt_info.get('changes', [])`
  - 建议: 使用 aiohttp

- **opt_info.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:407
  - 代码: `opt_info.get('improvement', '')`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:454
  - 代码: `node.metadata.get('tool')`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:501
  - 代码: `task.get('description', '')`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:502
  - 代码: `task.get('inputs', [])`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:503
  - 代码: `task.get('outputs', [])`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:504
  - 代码: `task.get('dependencies', [])`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\agents\decision_chain\unified_optimizer.py:505
  - 代码: `task.get('metadata', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:227
  - 代码: `result.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:228
  - 代码: `result.get('error_message')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:245
  - 代码: `result.get('confidence', 0.5)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:254
  - 代码: `result.get('goal', {'description': user_input})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:255
  - 代码: `result.get('constraints', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:277
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:286
  - 代码: `data.get('params', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:364
  - 代码: `result.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:371
  - 代码: `result.get('confidence', 0.5)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:376
  - 代码: `result.get('goal', {'description': user_input})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:377
  - 代码: `result.get('constraints', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:399
  - 代码: `data.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:406
  - 代码: `data.get('params', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:80
  - 代码: `payload.get('graph')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:81
  - 代码: `payload.get('data_pool')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:94
  - 代码: `payload.get('node')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:95
  - 代码: `payload.get('data_pool')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:179
  - 代码: `data_pool.get(output_key)`
  - 建议: 使用 aiohttp

- **tool_info.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:311
  - 代码: `tool_info.get('name', 'unknown')`
  - 建议: 使用 aiohttp

- **tool_info.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:313
  - 代码: `tool_info.get('priority', 100)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:353
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:355
  - 代码: `result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **time.sleep**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:381
  - 代码: `time.sleep(delay)`
  - 建议: 使用 asyncio.sleep

- **task_graph.get_ready_nodes**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:513
  - 代码: `task_graph.get_ready_nodes()`
  - 建议: 使用异步读取方法

- **result.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:553
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\node_scheduler\scheduler.py:558
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **prompts.get**
  - 位置: src\flood_decision_agent\agents\prompts\base_prompts.py:194
  - 代码: `prompts.get(agent_type, '你是一个专业的 AI 助手。')`
  - 建议: 使用 aiohttp

- **ChainGenerationPrompts.OPTIMIZER_STRATEGIES.get**
  - 位置: src\flood_decision_agent\agents\prompts\chain_generation_prompts.py:95
  - 代码: `ChainGenerationPrompts.OPTIMIZER_STRATEGIES.get(optimizer_strategy, ChainGenerationPrompts.OPTIMIZER_STRATEGIES['plan'])`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\prompts\chain_generation_prompts.py:116
  - 代码: `tool.get('description', '')`
  - 建议: 使用 aiohttp

- **file_guidance.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1399
  - 代码: `file_guidance.get(file_name, '')`
  - 建议: 使用 aiohttp

- **doc_requirements.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1472
  - 代码: `doc_requirements.get(doc_type, doc_requirements['plan'])`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1640
  - 代码: `context.get('user_input', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1641
  - 代码: `context.get('domain', '水利调度')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1642
  - 代码: `context.get('existing_content')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1643
  - 代码: `context.get('constraints')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1644
  - 代码: `context.get('references')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1650
  - 代码: `context.get('water_business_type')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1651
  - 代码: `context.get('use_water_domain_knowledge', True)`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1655
  - 代码: `context.get('section_name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1656
  - 代码: `context.get('current_content', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1657
  - 代码: `context.get('extra_context', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1664
  - 代码: `context.get('section_name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1665
  - 代码: `context.get('current_content', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1666
  - 代码: `context.get('extra_context', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1673
  - 代码: `context.get('file_name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1674
  - 代码: `context.get('section_name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1675
  - 代码: `context.get('current_content', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1676
  - 代码: `context.get('feature_context', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1681
  - 代码: `context.get('doc_type', 'plan')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1682
  - 代码: `context.get('content', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1686
  - 代码: `context.get('spec_content', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1687
  - 代码: `context.get('existing_tasks')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:1691
  - 代码: `context.get('plan_content', '')`
  - 建议: 使用 aiohttp

- **cls.DATA_CHAIN_TEMPLATES.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:520
  - 代码: `cls.DATA_CHAIN_TEMPLATES.get(chain_type)`
  - 建议: 使用 aiohttp

- **stage_info.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:533
  - 代码: `stage_info.get('inputs', [])`
  - 建议: 使用 aiohttp

- **stage_info.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:534
  - 代码: `stage_info.get('outputs', [])`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:583
  - 代码: `rule.get('constraint', '无')`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:584
  - 代码: `rule.get('rationale', '')`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\agents\prompts\water_domain_prompts.py:584
  - 代码: `rule.get('reference', '')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:155
  - 代码: `tool.get('name', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:193
  - 代码: `context.get('description', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:193
  - 代码: `context.get('user_input', '')`
  - 建议: 使用 aiohttp

- **task_tool_mapping.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:196
  - 代码: `task_tool_mapping.get(task_type, [task_type.lower()])`
  - 建议: 使用 aiohttp

- **tool_info.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:217
  - 代码: `tool_info.get('description', '')`
  - 建议: 使用 aiohttp

- **tool_spec.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:251
  - 代码: `tool_spec.get('server_name')`
  - 建议: 使用 aiohttp

- **tool_spec.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:252
  - 代码: `tool_spec.get('tool_config', {})`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:303
  - 代码: `data_pool.get('city')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:303
  - 代码: `data_pool.get('station')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:313
  - 代码: `data_pool.get('station')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:313
  - 代码: `data_pool.get('reservoir')`
  - 建议: 使用 aiohttp

- **concurrent.futures.ThreadPoolExecutor**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:331
  - 代码: `concurrent.futures.ThreadPoolExecutor()`
  - 建议: 使用异步读取方法

- **asyncio.run**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:338
  - 代码: `asyncio.run(self._process_async(message))`
  - 建议: 使用 asyncio.create_subprocess_exec

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:356
  - 代码: `payload.get('node_id', 'unknown')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:357
  - 代码: `payload.get('task_type', 'default')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:358
  - 代码: `payload.get('tools', [])`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:359
  - 代码: `payload.get('execution_strategy', 'auto')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:360
  - 代码: `payload.get('data_pool')`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:361
  - 代码: `payload.get('context', {})`
  - 建议: 使用 aiohttp

- **payload.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:362
  - 代码: `payload.get('data_dependencies', [])`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:448
  - 代码: `dep.get('data_key')`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:463
  - 代码: `dep.get('description', '')`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:464
  - 代码: `dep.get('required', True)`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:465
  - 代码: `dep.get('value_schema')`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:466
  - 代码: `dep.get('default_value')`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:467
  - 代码: `dep.get('validation_rules')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:496
  - 代码: `context.get('description', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:497
  - 代码: `context.get('required', True)`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:541
  - 代码: `context.get('allow_auto_select', True)`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:548
  - 代码: `tool.get('tool_name')`
  - 建议: 使用 aiohttp

- **multi_tool_tasks.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:621
  - 代码: `multi_tool_tasks.get(task_type, 1)`
  - 建议: 使用 aiohttp

- **hierarchy.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:672
  - 代码: `hierarchy.get(task_type, ['data_query'])`
  - 建议: 使用 aiohttp

- **tool_spec.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:747
  - 代码: `tool_spec.get('tool_config', {})`
  - 建议: 使用 aiohttp

- **tool_spec.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:748
  - 代码: `tool_spec.get('is_mcp_tool', False)`
  - 建议: 使用 aiohttp

- **concurrent.futures.ThreadPoolExecutor**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:758
  - 代码: `concurrent.futures.ThreadPoolExecutor()`
  - 建议: 使用异步读取方法

- **asyncio.run**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:763
  - 代码: `asyncio.run(self._execute_mcp_tool(tool_spec, data_pool))`
  - 建议: 使用 asyncio.create_subprocess_exec

- **t.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:817
  - 代码: `t.get('priority', 100)`
  - 建议: 使用 aiohttp

- **r.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:829
  - 代码: `r.get('success')`
  - 建议: 使用 aiohttp

- **r.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:835
  - 代码: `r.get('error')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:902
  - 代码: `data_pool.get('rainfall_forecast')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:913
  - 代码: `data_pool.get('inflow_forecast')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\executor.py:925
  - 代码: `data_pool.get('dispatch_plan')`
  - 建议: 使用 aiohttp

- **self._get_ready_tasks**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:163
  - 代码: `self._get_ready_tasks(nodes, executed_tasks)`
  - 建议: 使用异步读取方法

- **result.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:214
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:216
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:220
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:239
  - 代码: `result.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:333
  - 代码: `node.metadata.get('mcp_tools', [])`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:336
  - 代码: `tool.get('tool_name')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:338
  - 代码: `tool.get('server_name')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:339
  - 代码: `tool.get('is_mcp_tool', False)`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:340
  - 代码: `tool.get('priority', 80)`
  - 建议: 使用 aiohttp

- **node.metadata.get**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:390
  - 代码: `node.metadata.get('dependencies', [])`
  - 建议: 使用 aiohttp

- **ready.append**
  - 位置: src\flood_decision_agent\agents\task_executor\streaming_executor.py:396
  - 代码: `ready.append((node_id, node))`
  - 建议: 使用异步读取方法

- **scheduler.run**
  - 位置: src\flood_decision_agent\app\pipeline.py:38
  - 代码: `scheduler.run(graph=graph, data_pool=data_pool)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: src\flood_decision_agent\app\real_pipeline.py:77
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **node_info.get**
  - 位置: src\flood_decision_agent\app\real_pipeline.py:251
  - 代码: `node_info.get('node_id', f'node_{i}')`
  - 建议: 使用 aiohttp

- **node_info.get**
  - 位置: src\flood_decision_agent\app\real_pipeline.py:252
  - 代码: `node_info.get('task_type', 'default')`
  - 建议: 使用 aiohttp

- **r.get**
  - 位置: src\flood_decision_agent\app\real_pipeline.py:345
  - 代码: `r.get('status')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: src\flood_decision_agent\app\real_pipeline.py:376
  - 代码: `pipeline.run(user_input, context)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **task_request.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:131
  - 代码: `task_request.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **task_request.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:135
  - 代码: `task_request.get('input', '')`
  - 建议: 使用 aiohttp

- **task_request.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:185
  - 代码: `task_request.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **self.scheduler.run**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:207
  - 代码: `self.scheduler.run(graph=graph, data_pool=data_pool)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:210
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:228
  - 代码: `result.get('node_results', [])`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:320
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:325
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:331
  - 代码: `result.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:332
  - 代码: `result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: src\flood_decision_agent\app\visualized_pipeline.py:384
  - 代码: `pipeline.run(task_request)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **self._key_to_record_ids.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\service.py:140
  - 代码: `self._key_to_record_ids.get(data_key, [])`
  - 建议: 使用 aiohttp

- **self._records.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\service.py:206
  - 代码: `self._records.get(record_id)`
  - 建议: 使用 aiohttp

- **self._records.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\service.py:253
  - 代码: `self._records.get(record_id)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\detector.py:77
  - 代码: `open(file_path, 'rb')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\detector.py:78
  - 代码: `f.read(1024)`
  - 建议: 使用异步读取方法

- **self._read_from_path**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:55
  - 代码: `self._read_from_path(input_data, detected_format, **kwargs)`
  - 建议: 使用异步读取方法

- **self._read_from_bytes**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:59
  - 代码: `self._read_from_bytes(input_data, detected_format, **kwargs)`
  - 建议: 使用异步读取方法

- **pd.read_csv**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:174
  - 代码: `pd.read_csv(path, **kwargs)`
  - 建议: 使用异步读取方法

- **pd.read_excel**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:176
  - 代码: `pd.read_excel(path, **kwargs)`
  - 建议: 使用异步读取方法

- **pd.read_csv**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:199
  - 代码: `pd.read_csv(io.BytesIO(data), **kwargs)`
  - 建议: 使用异步读取方法

- **pd.read_excel**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\file.py:201
  - 代码: `pd.read_excel(io.BytesIO(data), **kwargs)`
  - 建议: 使用异步读取方法

- **csv.reader**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\table.py:50
  - 代码: `csv.reader(csv_file, delimiter=detected_delimiter)`
  - 建议: 使用异步读取方法

- **result.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\table.py:160
  - 代码: `result.get('content', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\adapters\table.py:174
  - 代码: `result.get('content', {})`
  - 建议: 使用 aiohttp

- **task_context.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:124
  - 代码: `task_context.get('task_id', str(uuid.uuid4()))`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:131
  - 代码: `dep.get('data_key', '')`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:132
  - 代码: `dep.get('is_required', True)`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:133
  - 代码: `dep.get('has_default', False)`
  - 建议: 使用 aiohttp

- **dep.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:144
  - 代码: `dep.get('description', f'需要提供数据: {data_key}')`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:198
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **schema.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:204
  - 代码: `schema.get('description', f'需要提供数据: {data_key}')`
  - 建议: 使用 aiohttp

- **session.add_request**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:212
  - 代码: `session.add_request(request)`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:259
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **session.get_request**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:264
  - 代码: `session.get_request(request_id)`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:292
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **session.get_request**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:297
  - 代码: `session.get_request(request_id)`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:327
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **session.get_request**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:332
  - 代码: `session.get_request(request_id)`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:370
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **session.get_request**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:375
  - 代码: `session.get_request(request_id)`
  - 建议: 使用 aiohttp

- **self._execution_callbacks.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:445
  - 代码: `self._execution_callbacks.get(session_id, [])`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:468
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **self._execution_paused.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:487
  - 代码: `self._execution_paused.get(session_id, False)`
  - 建议: 使用 aiohttp

- **self.sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\manager.py:520
  - 代码: `self.sessions.get(session_id)`
  - 建议: 使用 aiohttp

- **self._request_map.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\clarification\models.py:179
  - 代码: `self._request_map.get(request_id)`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confidence\rater.py:72
  - 代码: `metadata.get('has_original_file', True)`
  - 建议: 使用 aiohttp

- **self._confidence_scores.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confidence\rater.py:100
  - 代码: `self._confidence_scores.get(level, 0.0)`
  - 建议: 使用 aiohttp

- **self._confidence_colors.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confidence\rater.py:111
  - 代码: `self._confidence_colors.get(level, 'gray')`
  - 建议: 使用 aiohttp

- **self._confidence_icons.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confidence\rater.py:122
  - 代码: `self._confidence_icons.get(level, '?')`
  - 建议: 使用 aiohttp

- **prop_schema.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:178
  - 代码: `prop_schema.get('required')`
  - 建议: 使用 aiohttp

- **self._sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:234
  - 代码: `self._sessions.get(confirmation_id)`
  - 建议: 使用 aiohttp

- **user_response.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:238
  - 代码: `user_response.get('action', 'confirm')`
  - 建议: 使用 aiohttp

- **user_response.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:239
  - 代码: `user_response.get('notes', '')`
  - 建议: 使用 aiohttp

- **user_response.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:240
  - 代码: `user_response.get('modified_fields', {})`
  - 建议: 使用 aiohttp

- **original_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:266
  - 代码: `original_data.get(field_name)`
  - 建议: 使用 aiohttp

- **self._sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:313
  - 代码: `self._sessions.get(confirmation_id)`
  - 建议: 使用 aiohttp

- **self._sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:325
  - 代码: `self._sessions.get(confirmation_id)`
  - 建议: 使用 aiohttp

- **self._sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:344
  - 代码: `self._sessions.get(confirmation_id)`
  - 建议: 使用 aiohttp

- **self._sessions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:447
  - 代码: `self._sessions.get(confirmation_id)`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:484
  - 代码: `field_groups.get(DataFieldStatus.MISSING, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:499
  - 代码: `field_groups.get(DataFieldStatus.WARNING, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:514
  - 代码: `field_groups.get(DataFieldStatus.INVALID, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:529
  - 代码: `field_groups.get(DataFieldStatus.VALID, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:545
  - 代码: `field_groups.get(DataFieldStatus.MISSING, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:546
  - 代码: `field_groups.get(DataFieldStatus.WARNING, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:547
  - 代码: `field_groups.get(DataFieldStatus.INVALID, [])`
  - 建议: 使用 aiohttp

- **field_groups.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\confirmation\manager.py:548
  - 代码: `field_groups.get(DataFieldStatus.VALID, [])`
  - 建议: 使用 aiohttp

- **cls.ROUGHNESS_COEFFICIENTS.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:175
  - 代码: `cls.ROUGHNESS_COEFFICIENTS.get('人工渠道', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:176
  - 代码: `data.get(channel_type, {})`
  - 建议: 使用 aiohttp

- **channel_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:177
  - 代码: `channel_data.get(vegetation)`
  - 建议: 使用 aiohttp

- **cls.ROUGHNESS_COEFFICIENTS.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:180
  - 代码: `cls.ROUGHNESS_COEFFICIENTS.get('河道状况', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:181
  - 代码: `data.get(condition, {})`
  - 建议: 使用 aiohttp

- **condition_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:182
  - 代码: `condition_data.get(vegetation)`
  - 建议: 使用 aiohttp

- **cls.ROUGHNESS_COEFFICIENTS.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:185
  - 代码: `cls.ROUGHNESS_COEFFICIENTS.get('土壤类型', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:186
  - 代码: `data.get(soil_type, {})`
  - 建议: 使用 aiohttp

- **soil_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:187
  - 代码: `soil_data.get(vegetation)`
  - 建议: 使用 aiohttp

- **cls.RUNOFF_PARAMETERS.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:201
  - 代码: `cls.RUNOFF_PARAMETERS.get('径流系数', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:202
  - 代码: `data.get(land_use, {})`
  - 建议: 使用 aiohttp

- **land_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:204
  - 代码: `land_data.get(sub_type)`
  - 建议: 使用 aiohttp

- **cls.CHANNEL_PARAMETERS.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:221
  - 代码: `cls.CHANNEL_PARAMETERS.get(param_name, {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\config.py:223
  - 代码: `data.get(channel_size)`
  - 建议: 使用 aiohttp

- **soil_factors.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\formulas.py:76
  - 代码: `soil_factors.get(soil_type, 1.0)`
  - 建议: 使用 aiohttp

- **vegetation_factors.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\formulas.py:78
  - 代码: `vegetation_factors.get(vegetation, 1.0)`
  - 建议: 使用 aiohttp

- **condition_factors.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\formulas.py:80
  - 代码: `condition_factors.get(condition, 1.0)`
  - 建议: 使用 aiohttp

- **land_use_coefficients.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\formulas.py:155
  - 代码: `land_use_coefficients.get(land_use, 0.5)`
  - 建议: 使用 aiohttp

- **soil_adjustments.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\formulas.py:165
  - 代码: `soil_adjustments.get(soil_type, 0.0)`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:72
  - 代码: `conditions.get('soil_type')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:72
  - 代码: `conditions.get('土壤类型')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:73
  - 代码: `conditions.get('vegetation')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:73
  - 代码: `conditions.get('植被覆盖')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:74
  - 代码: `conditions.get('condition')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:74
  - 代码: `conditions.get('河道状况')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:75
  - 代码: `conditions.get('channel_type')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:75
  - 代码: `conditions.get('渠道类型')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:84
  - 代码: `conditions.get('land_use')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:84
  - 代码: `conditions.get('土地利用')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:85
  - 代码: `conditions.get('sub_type')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:85
  - 代码: `conditions.get('子类型')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:94
  - 代码: `conditions.get('param_name')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:94
  - 代码: `conditions.get('参数名')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:95
  - 代码: `conditions.get('channel_size')`
  - 建议: 使用 aiohttp

- **conditions.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:95
  - 代码: `conditions.get('河道规模')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:131
  - 代码: `params.get('soil_type')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:131
  - 代码: `params.get('土壤类型')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:132
  - 代码: `params.get('vegetation')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:132
  - 代码: `params.get('植被覆盖')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:133
  - 代码: `params.get('condition')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:133
  - 代码: `params.get('河道状况')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:140
  - 代码: `params.get('rainfall_duration')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:140
  - 代码: `params.get('降雨历时')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:141
  - 代码: `params.get('total_rainfall')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:141
  - 代码: `params.get('降雨总量')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:142
  - 代码: `params.get('basin_area')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:142
  - 代码: `params.get('流域面积')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:143
  - 代码: `params.get('runoff_coefficient')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:143
  - 代码: `params.get('径流系数')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:156
  - 代码: `params.get('land_use')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:156
  - 代码: `params.get('土地利用')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:157
  - 代码: `params.get('soil_type')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:157
  - 代码: `params.get('土壤类型')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:158
  - 代码: `params.get('slope')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:158
  - 代码: `params.get('坡度')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:165
  - 代码: `params.get('basin_length')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:165
  - 代码: `params.get('流域长度')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:166
  - 代码: `params.get('slope')`
  - 建议: 使用 aiohttp

- **params.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:166
  - 代码: `params.get('坡度')`
  - 建议: 使用 aiohttp

- **best_match.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:219
  - 代码: `best_match.get('name', '未知工程')`
  - 建议: 使用 aiohttp

- **best_match.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:221
  - 代码: `best_match.get('id', 'N/A')`
  - 建议: 使用 aiohttp

- **c.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\defaults\provider.py:313
  - 代码: `c.get('id')`
  - 建议: 使用 aiohttp

- **prompt_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:132
  - 代码: `prompt_data.get('prompt', '')`
  - 建议: 使用 aiohttp

- **extracted_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:133
  - 代码: `extracted_data.get('_raw_response', '')`
  - 建议: 使用 aiohttp

- **prompt_data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:234
  - 代码: `prompt_data.get('prompt', '')`
  - 建议: 使用 aiohttp

- **response.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:243
  - 代码: `response.get('text', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:446
  - 代码: `data.get(field_def.name)`
  - 建议: 使用 aiohttp

- **SCHEMA_REGISTRY.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\schema.py:446
  - 代码: `SCHEMA_REGISTRY.get(schema_type)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:130
  - 代码: `data.get('elevation', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:157
  - 代码: `data.get('left_bank_n', 1)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:157
  - 代码: `data.get('right_bank_n', 1)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:215
  - 代码: `data.get('peak_intensity', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:215
  - 代码: `data.get('rainfall_duration', 1)`
  - 建议: 使用 aiohttp

- **self.REASONABLENESS_RULES.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:367
  - 代码: `self.REASONABLENESS_RULES.get(schema_type, [])`
  - 建议: 使用 aiohttp

- **self._custom_rules.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:368
  - 代码: `self._custom_rules.get(schema_type, [])`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:378
  - 代码: `rule.get('depends_on', [])`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:398
  - 代码: `rule.get('level', ValidationLevel.ERROR)`
  - 建议: 使用 aiohttp

- **rule.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:404
  - 代码: `rule.get('suggestion', '请检查数值是否合理')`
  - 建议: 使用 aiohttp

- **error_codes.get**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\validator.py:544
  - 代码: `error_codes.get(issue.code, 0)`
  - 建议: 使用 aiohttp

- **self._conversations.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:82
  - 代码: `self._conversations.get(conversation_id)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:153
  - 代码: `result.get('response', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:154
  - 代码: `result.get('intent')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:155
  - 代码: `result.get('execution_result')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:161
  - 代码: `result.get('response', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:176
  - 代码: `result.get('response', '')`
  - 建议: 使用 aiohttp

- **context_analysis.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:206
  - 代码: `context_analysis.get('suggested_action', 'continue')`
  - 建议: 使用 aiohttp

- **flow_decision.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:277
  - 代码: `flow_decision.get('use_context')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: src\flood_decision_agent\conversation\manager.py:287
  - 代码: `pipeline.run({'type': 'natural_language', 'input': enhanced_input, 'conversation_context': state.get_full_context()})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **pipeline.run**
  - 位置: src\flood_decision_agent\conversation\manager.py:331
  - 代码: `pipeline.run({'type': 'natural_language', 'input': user_input, 'system_prompt': system_prompt})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.data_pool_snapshot.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:339
  - 代码: `result.data_pool_snapshot.get('intent', {})`
  - 建议: 使用 aiohttp

- **intent.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:340
  - 代码: `intent.get('task_type')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: src\flood_decision_agent\conversation\manager.py:375
  - 代码: `pipeline.run({'type': 'natural_language', 'input': enhanced_input, 'is_follow_up': True, 'original_task': state.current_task_type})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:432
  - 代码: `result.get('response', str(result))`
  - 建议: 使用 aiohttp

- **self._conversations.get**
  - 位置: src\flood_decision_agent\conversation\manager.py:454
  - 代码: `self._conversations.get(conversation_id)`
  - 建议: 使用 aiohttp

- **self._store.get**
  - 位置: src\flood_decision_agent\core\shared_data_pool.py:25
  - 代码: `self._store.get(key, default)`
  - 建议: 使用 aiohttp

- **ready_nodes.append**
  - 位置: src\flood_decision_agent\core\task_graph.py:190
  - 代码: `ready_nodes.append(node_id)`
  - 建议: 使用异步读取方法

- **self._nodes.get**
  - 位置: src\flood_decision_agent\core\task_graph.py:203
  - 代码: `self._nodes.get(node_id)`
  - 建议: 使用 aiohttp

- **self._edges.get**
  - 位置: src\flood_decision_agent\core\task_graph.py:241
  - 代码: `self._edges.get(node_id, [])`
  - 建议: 使用 aiohttp

- **BUSINESS_TO_EXECUTION_MAP.get**
  - 位置: src\flood_decision_agent\core\task_types.py:189
  - 代码: `BUSINESS_TO_EXECUTION_MAP.get(business_type, [ExecutionTaskType.DATA_COLLECTION])`
  - 建议: 使用 aiohttp

- **BUSINESS_TYPE_DESCRIPTIONS.get**
  - 位置: src\flood_decision_agent\core\task_types.py:201
  - 代码: `BUSINESS_TYPE_DESCRIPTIONS.get(business_type, business_type.value)`
  - 建议: 使用 aiohttp

- **EXECUTION_TYPE_DESCRIPTIONS.get**
  - 位置: src\flood_decision_agent\core\task_types.py:213
  - 代码: `EXECUTION_TYPE_DESCRIPTIONS.get(execution_type, execution_type.value)`
  - 建议: 使用 aiohttp

- **datasets.get**
  - 位置: src\flood_decision_agent\data\mock_data.py:28
  - 代码: `datasets.get('rainfall_forecast')`
  - 建议: 使用 aiohttp

- **datasets.get**
  - 位置: src\flood_decision_agent\data\mock_data.py:29
  - 代码: `datasets.get('inflow_forecast')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:116
  - 代码: `metadata.get('optimization', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:120
  - 代码: `metadata.get('intent', {})`
  - 建议: 使用 aiohttp

- **intent_data.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:125
  - 代码: `intent_data.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:149
  - 代码: `execution_result.get('completed_count', 0)`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:178
  - 代码: `metadata.get('optimization', {})`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:224
  - 代码: `execution_result.get('results', {})`
  - 建议: 使用 aiohttp

- **node_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:225
  - 代码: `node_result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:228
  - 代码: `metrics.get('tools_used', [])`
  - 建议: 使用 aiohttp

- **self.robustness.record_tool_call**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:230
  - 代码: `self.robustness.record_tool_call(tool_name=tool_name, success=node_result.get('status') == 'success')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **node_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:232
  - 代码: `node_result.get('status')`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:236
  - 代码: `metrics.get('retry_count', 0)`
  - 建议: 使用 aiohttp

- **node_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:241
  - 代码: `node_result.get('status')`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:245
  - 代码: `metrics.get('execution_strategy', 'auto')`
  - 建议: 使用 aiohttp

- **node_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:250
  - 代码: `node_result.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:259
  - 代码: `execution_result.get('status')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:285
  - 代码: `metadata.get('optimization', {})`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:291
  - 代码: `execution_result.get('status')`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:295
  - 代码: `execution_result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **execution_result.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:300
  - 代码: `execution_result.get('status')`
  - 建议: 使用 aiohttp

- **human_scores.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:431
  - 代码: `human_scores.get(case.id)`
  - 建议: 使用 aiohttp

- **result.metrics.get**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:469
  - 代码: `result.metrics.get('reliability_score', 0.0)`
  - 建议: 使用 aiohttp

- **self._metrics.get**
  - 位置: src\flood_decision_agent\evaluation\core\registry.py:57
  - 代码: `self._metrics.get(name)`
  - 建议: 使用 aiohttp

- **self._loaders.get**
  - 位置: src\flood_decision_agent\evaluation\core\registry.py:88
  - 代码: `self._loaders.get(name)`
  - 建议: 使用 aiohttp

- **self._formatters.get**
  - 位置: src\flood_decision_agent\evaluation\core\registry.py:112
  - 代码: `self._formatters.get(name)`
  - 建议: 使用 aiohttp

- **self._validators.get**
  - 位置: src\flood_decision_agent\evaluation\core\registry.py:136
  - 代码: `self._validators.get(name)`
  - 建议: 使用 aiohttp

- **self._hooks.get**
  - 位置: src\flood_decision_agent\evaluation\core\registry.py:175
  - 代码: `self._hooks.get(event, [])`
  - 建议: 使用 aiohttp

- **self.run**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:156
  - 代码: `self.run(suite)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **self.run**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:199
  - 代码: `self.run(new_suite)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **run.summary.get**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:224
  - 代码: `run.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **run.summary.get**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:225
  - 代码: `run.summary.get('total', 0)`
  - 建议: 使用 aiohttp

- **run.summary.get**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:226
  - 代码: `run.summary.get('passed', 0)`
  - 建议: 使用 aiohttp

- **first.summary.get**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:234
  - 代码: `first.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **last.summary.get**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:235
  - 代码: `last.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\core\runner.py:285
  - 代码: `open(file_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:102
  - 代码: `summary.get('total', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:103
  - 代码: `summary.get('passed', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:104
  - 代码: `summary.get('failed', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:105
  - 代码: `summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **stats.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:115
  - 代码: `stats.get('total', 0)`
  - 建议: 使用 aiohttp

- **stats.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:116
  - 代码: `stats.get('passed', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:152
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:154
  - 代码: `result.get('test_case_id', '-')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:155
  - 代码: `result.get('test_case_name', '-')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:157
  - 代码: `result.get('execution_time_ms', 0)`
  - 建议: 使用 aiohttp

- **translations.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:183
  - 代码: `translations.get(category, category)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:201
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:202
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **self.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:245
  - 代码: `self.summary.get('total', 0)`
  - 建议: 使用 aiohttp

- **self.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:246
  - 代码: `self.summary.get('passed', 0)`
  - 建议: 使用 aiohttp

- **self.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:247
  - 代码: `self.summary.get('failed', 0)`
  - 建议: 使用 aiohttp

- **self.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:248
  - 代码: `self.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:304
  - 代码: `dimension_scores.get(dim, 0.0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:318
  - 代码: `result.get('test_results', [])`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:333
  - 代码: `dimension_scores.get('effectiveness', 1.0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:336
  - 代码: `dimension_scores.get('efficiency', 1.0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:339
  - 代码: `dimension_scores.get('robustness', 1.0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:342
  - 代码: `dimension_scores.get('safety', 1.0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:345
  - 代码: `dimension_scores.get('autonomy', 1.0)`
  - 建议: 使用 aiohttp

- **dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:348
  - 代码: `dimension_scores.get('explainability', 1.0)`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:352
  - 代码: `metrics.get('effectiveness', {})`
  - 建议: 使用 aiohttp

- **effectiveness.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:353
  - 代码: `effectiveness.get('task_success_rate', MetricValue('', 1.0))`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:356
  - 代码: `metrics.get('efficiency', {})`
  - 建议: 使用 aiohttp

- **efficiency.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:357
  - 代码: `efficiency.get('avg_response_time', MetricValue('', 0.0))`
  - 建议: 使用 aiohttp

- **metrics.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:360
  - 代码: `metrics.get('robustness', {})`
  - 建议: 使用 aiohttp

- **robustness.get**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:361
  - 代码: `robustness.get('tool_failure_rate', MetricValue('', 0.0))`
  - 建议: 使用 aiohttp

- **csv.writer**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:25
  - 代码: `csv.writer(output)`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:28
  - 代码: `writer.writerow(['指标', '值'])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:31
  - 代码: `writer.writerow(['报告ID', report.report_id])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:32
  - 代码: `writer.writerow(['生成时间', report.created_at])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:33
  - 代码: `writer.writerow(['Agent版本', report.agent_version])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:34
  - 代码: `writer.writerow(['综合评分', f'{report.overall_score:.4f}'])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:35
  - 代码: `writer.writerow(['总测试数', report.summary.get('total', 0)])`
  - 建议: 使用异步写入方法

- **report.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:35
  - 代码: `report.summary.get('total', 0)`
  - 建议: 使用 aiohttp

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:36
  - 代码: `writer.writerow(['通过数', report.summary.get('passed', 0)])`
  - 建议: 使用异步写入方法

- **report.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:36
  - 代码: `report.summary.get('passed', 0)`
  - 建议: 使用 aiohttp

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:37
  - 代码: `writer.writerow(['失败数', report.summary.get('failed', 0)])`
  - 建议: 使用异步写入方法

- **report.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:37
  - 代码: `report.summary.get('failed', 0)`
  - 建议: 使用 aiohttp

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:38
  - 代码: `writer.writerow(['通过率', f"{report.summary.get('pass_rate', 0):.4f}"])`
  - 建议: 使用异步写入方法

- **report.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:38
  - 代码: `report.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **csv.writer**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:52
  - 代码: `csv.writer(output)`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:55
  - 代码: `writer.writerow(['类别', '指标', '值', '单位', '说明'])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:60
  - 代码: `writer.writerow([category, name, metric.value, metric.unit, metric.description])`
  - 建议: 使用异步写入方法

- **csv.writer**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:80
  - 代码: `csv.writer(output)`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:83
  - 代码: `writer.writerow(['测试ID', '名称', '状态', '耗时(ms)', '错误信息'])`
  - 建议: 使用异步写入方法

- **writer.writerow**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:87
  - 代码: `writer.writerow([result.get('test_case_id', ''), result.get('test_case_name', ''), '通过' if result.get('success') else '失败', result.get('execution_time_ms', 0), result.get('error_message', '')])`
  - 建议: 使用异步写入方法

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:88
  - 代码: `result.get('test_case_id', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:89
  - 代码: `result.get('test_case_name', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:90
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:91
  - 代码: `result.get('execution_time_ms', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:92
  - 代码: `result.get('error_message', '')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:114
  - 代码: `open(filepath, 'w', encoding='utf-8', newline='')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\csv_formatter.py:115
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\json_formatter.py:35
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\json_formatter.py:36
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\markdown_formatter.py:32
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\markdown_formatter.py:33
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **report.summary.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\markdown_formatter.py:55
  - 代码: `report.summary.get('pass_rate', 0)`
  - 建议: 使用 aiohttp

- **r.dimension_scores.get**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\markdown_formatter.py:70
  - 代码: `r.dimension_scores.get(dimension, 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:21
  - 代码: `data.get('overall_score', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:30
  - 代码: `data.get('report_id', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:231
  - 代码: `data.get('report_id', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:232
  - 代码: `data.get('created_at', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:233
  - 代码: `data.get('agent_version', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:247
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:251
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:255
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:259
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:266
  - 代码: `data.get('dimension_scores', {{}})`
  - 建议: 使用 aiohttp

- **translations.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\default_template.py:289
  - 代码: `translations.get(key, key)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\minimal_template.py:21
  - 代码: `data.get('overall_score', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\minimal_template.py:64
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\minimal_template.py:65
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\minimal_template.py:66
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\reports\templates\minimal_template.py:67
  - 代码: `data.get('summary', {{}})`
  - 建议: 使用 aiohttp

- **self.state.get**
  - 位置: src\flood_decision_agent\evaluation\scenarios\base.py:33
  - 代码: `self.state.get(key, default)`
  - 建议: 使用 aiohttp

- **cls._scenarios.get**
  - 位置: src\flood_decision_agent\evaluation\scenarios\base.py:119
  - 代码: `cls._scenarios.get(name)`
  - 建议: 使用 aiohttp

- **cls.get**
  - 位置: src\flood_decision_agent\evaluation\scenarios\base.py:129
  - 代码: `cls.get(name)`
  - 建议: 使用 aiohttp

- **self.config.get**
  - 位置: src\flood_decision_agent\evaluation\scenarios\flood_scenarios.py:34
  - 代码: `self.config.get('default_cases', True)`
  - 建议: 使用 aiohttp

- **self.config.get**
  - 位置: src\flood_decision_agent\evaluation\scenarios\flood_scenarios.py:300
  - 代码: `self.config.get('emergency_level', 'high')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:114
  - 代码: `data.get('expected', {})`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:116
  - 代码: `expected_data.get('success', True)`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:117
  - 代码: `expected_data.get('expected_intent')`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:118
  - 代码: `expected_data.get('expected_task_type')`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:119
  - 代码: `expected_data.get('expected_outputs', [])`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:120
  - 代码: `expected_data.get('expected_node_count_range', [0, 100])`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:121
  - 代码: `expected_data.get('min_reliability_score', 0.0)`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:122
  - 代码: `expected_data.get('max_response_time_ms', 30000.0)`
  - 建议: 使用 aiohttp

- **expected_data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:123
  - 代码: `expected_data.get('required_rules', [])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:129
  - 代码: `data.get('description', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:130
  - 代码: `data.get('case_type', 'positive')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:131
  - 代码: `data.get('priority', 3)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:132
  - 代码: `data.get('input_text', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:133
  - 代码: `data.get('structured_input')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:134
  - 代码: `data.get('input_type', 'natural_language')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:136
  - 代码: `data.get('reference_solution')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:137
  - 代码: `data.get('tags', [])`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:232
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:238
  - 代码: `open(filepath, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:241
  - 代码: `data.get('name', 'default')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:242
  - 代码: `data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\base.py:244
  - 代码: `data.get('test_cases', [])`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:34
  - 代码: `open(path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **combined.metadata.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:53
  - 代码: `combined.metadata.get('sources', [])`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:94
  - 代码: `open(path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:101
  - 代码: `data.get('name', 'unnamed')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:102
  - 代码: `data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\json_loader.py:104
  - 代码: `data.get('test_cases', [])`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:41
  - 代码: `open(path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **combined.metadata.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:53
  - 代码: `combined.metadata.get('sources', [])`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:83
  - 代码: `open(path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:90
  - 代码: `data.get('name', 'unnamed')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:91
  - 代码: `data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\evaluation\test_cases\loaders\yaml_loader.py:93
  - 代码: `data.get('test_cases', [])`
  - 建议: 使用 aiohttp

- **file_path.read_text**
  - 位置: src\flood_decision_agent\infrastructure\config_loader.py:93
  - 代码: `file_path.read_text(encoding='utf-8')`
  - 建议: 使用异步读取方法

- **os.environ.get**
  - 位置: src\flood_decision_agent\infrastructure\llm\kimi_client.py:28
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: src\flood_decision_agent\infrastructure\llm\kimi_client.py:88
  - 代码: `kwargs.get('temperature', self.temperature)`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: src\flood_decision_agent\infrastructure\llm\kimi_client.py:89
  - 代码: `kwargs.get('max_tokens', self.max_tokens)`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: src\flood_decision_agent\infrastructure\llm\kimi_client.py:104
  - 代码: `kwargs.get('temperature', self.temperature)`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: src\flood_decision_agent\infrastructure\llm\kimi_client.py:105
  - 代码: `kwargs.get('max_tokens', self.max_tokens)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:58
  - 代码: `open(content_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:59
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:69
  - 代码: `open(metadata_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:97
  - 代码: `open(content_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:98
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:103
  - 代码: `open(metadata_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **doc_data.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:158
  - 代码: `doc_data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:169
  - 代码: `metadata.get('status')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:175
  - 代码: `metadata.get('created_at')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:176
  - 代码: `metadata.get('updated_at')`
  - 建议: 使用 aiohttp

- **x.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:180
  - 代码: `x.get('updated_at', '')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:208
  - 代码: `open(messages_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:220
  - 代码: `open(metadata_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:247
  - 代码: `open(messages_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:253
  - 代码: `open(metadata_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **x.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:292
  - 代码: `x.get('updated_at', '')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:322
  - 代码: `open(tasks_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:328
  - 代码: `open(events_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:334
  - 代码: `open(context_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:363
  - 代码: `open(tasks_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:370
  - 代码: `open(events_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:377
  - 代码: `open(context_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **task_data.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:406
  - 代码: `task_data.get('tasks', [])`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:408
  - 代码: `task.get('id')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:418
  - 代码: `task_data.get('events')`
  - 建议: 使用 aiohttp

- **task_data.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\file_storage.py:419
  - 代码: `task_data.get('context')`
  - 建议: 使用 aiohttp

- **self._conversations.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\repositories\conversation_repo.py:14
  - 代码: `self._conversations.get(conversation_id)`
  - 建议: 使用 aiohttp

- **self._decisions.get**
  - 位置: src\flood_decision_agent\infrastructure\persistence\repositories\decision_repo.py:14
  - 代码: `self._decisions.get(decision_id)`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\mcp\adapters\tool_adapter.py:84
  - 代码: `data_pool.get(pool_key)`
  - 建议: 使用 aiohttp

- **task_keywords.get**
  - 位置: src\flood_decision_agent\mcp\adapters\tool_adapter.py:114
  - 代码: `task_keywords.get(task_type, [task_type])`
  - 建议: 使用 aiohttp

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:49
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:153
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **open**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:188
  - 代码: `open(config_file, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:192
  - 代码: `open(config_file, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:196
  - 代码: `config.get('mcp_servers')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:196
  - 代码: `config.get('mcpServers', {})`
  - 建议: 使用 aiohttp

- **server_config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:199
  - 代码: `server_config.get('enabled', True)`
  - 建议: 使用 aiohttp

- **server_config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:203
  - 代码: `server_config.get('command')`
  - 建议: 使用 aiohttp

- **server_config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:204
  - 代码: `server_config.get('args', [])`
  - 建议: 使用 aiohttp

- **server_config.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:205
  - 代码: `server_config.get('env', {})`
  - 建议: 使用 aiohttp

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:224
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **merged_env.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:225
  - 代码: `merged_env.get('PYTHONIOENCODING', 'utf-8')`
  - 建议: 使用 aiohttp

- **merged_env.get**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:230
  - 代码: `merged_env.get('PYTHONPATH', '')`
  - 建议: 使用 aiohttp

- **self.send_request**
  - 位置: src\flood_decision_agent\mcp\core\client.py:184
  - 代码: `self.send_request(request)`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: src\flood_decision_agent\mcp\core\client.py:202
  - 代码: `asyncio.sleep(self.config.retry_delay)`
  - 建议: 使用 asyncio.sleep

- **self._clients.get**
  - 位置: src\flood_decision_agent\mcp\core\client.py:306
  - 代码: `self._clients.get(name)`
  - 建议: 使用 aiohttp

- **self._clients.get**
  - 位置: src\flood_decision_agent\mcp\core\client.py:354
  - 代码: `self._clients.get(client_name)`
  - 建议: 使用 aiohttp

- **self._tools.get**
  - 位置: src\flood_decision_agent\mcp\core\server.py:147
  - 代码: `self._tools.get(name)`
  - 建议: 使用 aiohttp

- **self._do_send_request**
  - 位置: src\flood_decision_agent\mcp\core\session.py:241
  - 代码: `self._do_send_request(request, request_id)`
  - 建议: 使用 aiohttp

- **self._pending_requests.get**
  - 位置: src\flood_decision_agent\mcp\core\session.py:270
  - 代码: `self._pending_requests.get(request_id)`
  - 建议: 使用 aiohttp

- **self._handlers.get**
  - 位置: src\flood_decision_agent\mcp\core\session.py:303
  - 代码: `self._handlers.get(event, [])`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: src\flood_decision_agent\mcp\core\session.py:322
  - 代码: `asyncio.sleep(self.heartbeat_interval)`
  - 建议: 使用 asyncio.sleep

- **asyncio.sleep**
  - 位置: src\flood_decision_agent\mcp\core\session.py:339
  - 代码: `asyncio.sleep(5.0)`
  - 建议: 使用 asyncio.sleep

- **message_dict.get**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:180
  - 代码: `message_dict.get('message_type')`
  - 建议: 使用 aiohttp

- **message_dict.get**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:181
  - 代码: `message_dict.get('payload', {})`
  - 建议: 使用 aiohttp

- **message_dict.get**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:182
  - 代码: `message_dict.get('metadata', {})`
  - 建议: 使用 aiohttp

- **self._writer.close**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:258
  - 代码: `self._writer.close()`
  - 建议: 使用异步写入方法

- **self._writer.wait_closed**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:260
  - 代码: `self._writer.wait_closed()`
  - 建议: 使用异步写入方法

- **sys.stdout.buffer.write**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:271
  - 代码: `sys.stdout.buffer.write(header)`
  - 建议: 使用异步写入方法

- **sys.stdout.buffer.write**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:272
  - 代码: `sys.stdout.buffer.write(data)`
  - 建议: 使用异步写入方法

- **self._reader.readline**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:283
  - 代码: `self._reader.readline()`
  - 建议: 使用异步读取方法

- **self._reader.readexactly**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:302
  - 代码: `self._reader.readexactly(content_length)`
  - 建议: 使用异步读取方法

- **self._receive_queue.get**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:347
  - 代码: `self._receive_queue.get()`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\messages.py:119
  - 代码: `data.get('message_type', 'REQUEST')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\messages.py:124
  - 代码: `data.get('payload', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\messages.py:125
  - 代码: `data.get('metadata', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\types.py:63
  - 代码: `data.get('name', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\types.py:64
  - 代码: `data.get('description', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\types.py:65
  - 代码: `data.get('input_schema', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\protocol\types.py:66
  - 代码: `data.get('server_name', '')`
  - 建议: 使用 aiohttp

- **_handle_read_plan**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:359
  - 代码: `_handle_read_plan(arguments)`
  - 建议: 使用异步读取方法

- **_handle_read_spec**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:365
  - 代码: `_handle_read_spec(arguments)`
  - 建议: 使用异步读取方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:396
  - 代码: `args.get('notes', '')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:397
  - 代码: `args.get('output_path')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:425
  - 代码: `open(output_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:426
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:450
  - 代码: `open(plan_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:451
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:483
  - 代码: `open(plan_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:484
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:490
  - 代码: `open(plan_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:491
  - 代码: `f.write(updated_content)`
  - 建议: 使用异步写入方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:512
  - 代码: `args.get('technical_design', '待补充')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:513
  - 代码: `args.get('interfaces', '待补充')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:514
  - 代码: `args.get('acceptance_criteria', '待补充')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:515
  - 代码: `args.get('tasks', '待补充')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:535
  - 代码: `open(spec_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:536
  - 代码: `f.write(spec_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:548
  - 代码: `open(tasks_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:549
  - 代码: `f.write(tasks_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:563
  - 代码: `open(checklist_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:564
  - 代码: `f.write(checklist_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:590
  - 代码: `open(spec_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:591
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:622
  - 代码: `open(spec_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:623
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:629
  - 代码: `open(spec_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:630
  - 代码: `f.write(updated_content)`
  - 建议: 使用异步写入方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:647
  - 代码: `args.get('limit', 50)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:660
  - 代码: `open(filepath, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.readline**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:661
  - 代码: `f.readline()`
  - 建议: 使用异步读取方法

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:822
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:828
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:836
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **_handle_read_docx_content**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:147
  - 代码: `_handle_read_docx_content(arguments)`
  - 建议: 使用异步读取方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:177
  - 代码: `args.get('output_file')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:178
  - 代码: `args.get('include_metadata', True)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:245
  - 代码: `open(output_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:246
  - 代码: `f.write(markdown_content)`
  - 建议: 使用异步写入方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:351
  - 代码: `args.get('directory', 'data')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:352
  - 代码: `args.get('extension', '.docx')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:397
  - 代码: `args.get('filename', 'sample.docx')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:398
  - 代码: `args.get('title', '示例文档')`
  - 建议: 使用 aiohttp

- **para.add_run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:419
  - 代码: `para.add_run('支持 ')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **para.add_run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:420
  - 代码: `para.add_run('粗体')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **para.add_run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:421
  - 代码: `para.add_run(' 和 ')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **para.add_run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:422
  - 代码: `para.add_run('斜体')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **para.add_run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:423
  - 代码: `para.add_run(' 文本。')`
  - 建议: 使用 asyncio.create_subprocess_exec

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:473
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:481
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **_handle_write_planning**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:202
  - 代码: `_handle_write_planning(arguments)`
  - 建议: 使用异步写入方法

- **_handle_read_planning**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:204
  - 代码: `_handle_read_planning(arguments)`
  - 建议: 使用异步读取方法

- **_handle_write_data_json**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:212
  - 代码: `_handle_write_data_json(arguments)`
  - 建议: 使用异步写入方法

- **_handle_read_data_json**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:214
  - 代码: `_handle_read_data_json(arguments)`
  - 建议: 使用异步读取方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:231
  - 代码: `args.get('metadata', {})`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:232
  - 代码: `args.get('output_dir', PLANS_DIR)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:266
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:267
  - 代码: `f.write(full_content)`
  - 建议: 使用异步写入方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:284
  - 代码: `args.get('parse_metadata', True)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:300
  - 代码: `open(filepath, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:301
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:339
  - 代码: `args.get('filter', '')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:340
  - 代码: `args.get('limit', 100)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:381
  - 代码: `open(filepath, 'a', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:382
  - 代码: `f.write('\n\n')`
  - 建议: 使用异步写入方法

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:383
  - 代码: `f.write(f'<!-- Appended at {datetime.now().isoformat()} -->\n')`
  - 建议: 使用异步写入方法

- **f.write**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:384
  - 代码: `f.write(content)`
  - 建议: 使用异步写入方法

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:420
  - 代码: `args.get('indent', 2)`
  - 建议: 使用 aiohttp

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:428
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:451
  - 代码: `open(filepath, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:476
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:484
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:105
  - 代码: `inputs.get('rainfall', [])`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:106
  - 代码: `inputs.get('catchment_area', 100)`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:133
  - 代码: `inputs.get('inflow', [])`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:134
  - 代码: `inputs.get('k', 3.0)`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:135
  - 代码: `inputs.get('x', 0.3)`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:169
  - 代码: `inputs.get('inflow', [])`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:170
  - 代码: `inputs.get('initial_level', 100.0)`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:171
  - 代码: `inputs.get('target_level', 95.0)`
  - 建议: 使用 aiohttp

- **inputs.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:172
  - 代码: `inputs.get('max_outflow', 1000.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:486
  - 代码: `args.get('rainfall', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:487
  - 代码: `args.get('catchment_area', 100)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:488
  - 代码: `args.get('timestamps', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:489
  - 代码: `args.get('station_id', 'unknown')`
  - 建议: 使用 aiohttp

- **model.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:492
  - 代码: `model.run(inputs)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:514
  - 代码: `args.get('inflow', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:515
  - 代码: `args.get('k', 3.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:516
  - 代码: `args.get('x', 0.3)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:517
  - 代码: `args.get('reach_length', 10.0)`
  - 建议: 使用 aiohttp

- **model.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:520
  - 代码: `model.run(inputs)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:543
  - 代码: `args.get('inflow', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:544
  - 代码: `args.get('initial_level', 100.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:545
  - 代码: `args.get('target_level', 95.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:546
  - 代码: `args.get('max_outflow', 1000.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:547
  - 代码: `args.get('min_outflow', 10.0)`
  - 建议: 使用 aiohttp

- **model.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:550
  - 代码: `model.run(inputs)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:570
  - 代码: `args.get('forecast_inflow', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:571
  - 代码: `args.get('current_state', {})`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:572
  - 代码: `args.get('constraints', {})`
  - 建议: 使用 aiohttp

- **model.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:580
  - 代码: `model.run({'inflow': forecast_inflow, 'initial_level': current_state.get('water_level', 100.0), 'target_level': constraints.get('target_level', 95.0), 'max_outflow': constraints.get('max_outflow', 1000.0)})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **current_state.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:582
  - 代码: `current_state.get('water_level', 100.0)`
  - 建议: 使用 aiohttp

- **constraints.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:583
  - 代码: `constraints.get('target_level', 95.0)`
  - 建议: 使用 aiohttp

- **constraints.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:584
  - 代码: `constraints.get('max_outflow', 1000.0)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:609
  - 代码: `args.get('dispatch_plan', {})`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:610
  - 代码: `args.get('safety_rules', [])`
  - 建议: 使用 aiohttp

- **dispatch_plan.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:616
  - 代码: `dispatch_plan.get('outflow_schedule', [])`
  - 建议: 使用 aiohttp

- **dispatch_plan.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:626
  - 代码: `dispatch_plan.get('expected_final_level', 0)`
  - 建议: 使用 aiohttp

- **dispatch_plan.get**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:639
  - 代码: `dispatch_plan.get('plan_id', 'unknown')`
  - 建议: 使用 aiohttp

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:650
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:658
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:100
  - 代码: `os.environ.get('OPENWEATHER_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:103
  - 代码: `os.environ.get('QWEATHER_API_KEY')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:266
  - 代码: `args.get('provider', 'auto')`
  - 建议: 使用 aiohttp

- **_fetch_openweather_current**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:279
  - 代码: `_fetch_openweather_current(session, city)`
  - 建议: 使用 aiofiles 替代

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:292
  - 代码: `args.get('days', 3)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:293
  - 代码: `args.get('provider', 'auto')`
  - 建议: 使用 aiohttp

- **_fetch_openweather_forecast**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:305
  - 代码: `_fetch_openweather_forecast(session, city, days)`
  - 建议: 使用 aiofiles 替代

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:318
  - 代码: `args.get('hours', 12)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:319
  - 代码: `args.get('provider', 'auto')`
  - 建议: 使用 aiohttp

- **_fetch_openweather_hourly**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:331
  - 代码: `_fetch_openweather_hourly(session, city, hours)`
  - 建议: 使用 aiofiles 替代

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:345
  - 代码: `args.get('provider', 'auto')`
  - 建议: 使用 aiohttp

- **_fetch_openweather_by_coords**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:357
  - 代码: `_fetch_openweather_by_coords(session, lat, lon)`
  - 建议: 使用 aiofiles 替代

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:413
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:421
  - 代码: `data.get('rain', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:422
  - 代码: `data.get('weather', [{}])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:427
  - 代码: `data.get('name')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:428
  - 代码: `data.get('sys', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:431
  - 代码: `data.get('main', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:432
  - 代码: `data.get('main', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:433
  - 代码: `data.get('main', {})`
  - 建议: 使用 aiohttp

- **weather.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:434
  - 代码: `weather.get('description')`
  - 建议: 使用 aiohttp

- **weather.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:435
  - 代码: `weather.get('id')`
  - 建议: 使用 aiohttp

- **rain_data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:436
  - 代码: `rain_data.get('1h', 0)`
  - 建议: 使用 aiohttp

- **rain_data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:437
  - 代码: `rain_data.get('3h', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:440
  - 代码: `data.get('coord', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:441
  - 代码: `data.get('coord', {})`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:461
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:470
  - 代码: `data.get('list', [])`
  - 建议: 使用 aiohttp

- **item.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:471
  - 代码: `item.get('rain', {})`
  - 建议: 使用 aiohttp

- **item.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:472
  - 代码: `item.get('weather', [{}])`
  - 建议: 使用 aiohttp

- **item.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:474
  - 代码: `item.get('dt_txt')`
  - 建议: 使用 aiohttp

- **item.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:475
  - 代码: `item.get('main', {})`
  - 建议: 使用 aiohttp

- **weather.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:476
  - 代码: `weather.get('description')`
  - 建议: 使用 aiohttp

- **rain_data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:477
  - 代码: `rain_data.get('3h', 0)`
  - 建议: 使用 aiohttp

- **item.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:478
  - 代码: `item.get('pop', 0)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:484
  - 代码: `data.get('city', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:485
  - 代码: `data.get('city', {})`
  - 建议: 使用 aiohttp

- **_fetch_openweather_forecast**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:495
  - 代码: `_fetch_openweather_forecast(session, city, hours // 8 + 1)`
  - 建议: 使用 aiofiles 替代

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:513
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:520
  - 代码: `data.get('rain', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:521
  - 代码: `data.get('weather', [{}])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:528
  - 代码: `data.get('name')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:530
  - 代码: `data.get('main', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:531
  - 代码: `data.get('main', {})`
  - 建议: 使用 aiohttp

- **weather.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:532
  - 代码: `weather.get('description')`
  - 建议: 使用 aiohttp

- **rain_data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:533
  - 代码: `rain_data.get('1h', 0)`
  - 建议: 使用 aiohttp

- **rain_data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:534
  - 代码: `rain_data.get('3h', 0)`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:558
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:565
  - 代码: `data.get('now', {})`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:573
  - 代码: `now.get('temp')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:574
  - 代码: `now.get('humidity')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:575
  - 代码: `now.get('pressure')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:576
  - 代码: `now.get('text')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:577
  - 代码: `now.get('icon')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:578
  - 代码: `now.get('precip')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:579
  - 代码: `now.get('windSpeed')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:580
  - 代码: `now.get('windDir')`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:601
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:608
  - 代码: `data.get('daily', [])`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:612
  - 代码: `day.get('fxDate')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:613
  - 代码: `day.get('tempMax')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:614
  - 代码: `day.get('tempMin')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:615
  - 代码: `day.get('textDay')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:616
  - 代码: `day.get('textNight')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:617
  - 代码: `day.get('precip')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:618
  - 代码: `day.get('humidity')`
  - 建议: 使用 aiohttp

- **day.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:619
  - 代码: `day.get('windSpeedDay')`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:648
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:655
  - 代码: `data.get('hourly', [])`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:659
  - 代码: `hour.get('fxTime')`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:660
  - 代码: `hour.get('temp')`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:661
  - 代码: `hour.get('text')`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:662
  - 代码: `hour.get('precip')`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:663
  - 代码: `hour.get('humidity')`
  - 建议: 使用 aiohttp

- **hour.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:664
  - 代码: `hour.get('windSpeed')`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:692
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:699
  - 代码: `data.get('now', {})`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:707
  - 代码: `now.get('temp')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:708
  - 代码: `now.get('humidity')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:709
  - 代码: `now.get('text')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:710
  - 代码: `now.get('precip')`
  - 建议: 使用 aiohttp

- **now.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:711
  - 代码: `now.get('windSpeed')`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:735
  - 代码: `session.get(url, params=params)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:740
  - 代码: `data.get('location', [])`
  - 建议: 使用 aiohttp

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:751
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:757
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:765
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:40
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:206
  - 代码: `args.get('num_results', 5)`
  - 建议: 使用 aiohttp

- **session.post**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:247
  - 代码: `session.post(f'{KIMI_API_BASE}/chat/completions', headers=headers, json=payload, timeout=30)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:270
  - 代码: `message.get('content', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:273
  - 代码: `message.get('citations', [])`
  - 建议: 使用 aiohttp

- **citation.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:282
  - 代码: `citation.get('title', '未知标题')`
  - 建议: 使用 aiohttp

- **citation.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:283
  - 代码: `citation.get('url', '')`
  - 建议: 使用 aiohttp

- **citation.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:284
  - 代码: `citation.get('content', '')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:308
  - 代码: `args.get('max_length', 5000)`
  - 建议: 使用 aiohttp

- **session.post**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:371
  - 代码: `session.post(f'{KIMI_API_BASE}/chat/completions', headers=headers, json=payload, timeout=30)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:391
  - 代码: `message.get('content', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:398
  - 代码: `message.get('citations', [])`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:421
  - 代码: `args.get('days', 7)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:422
  - 代码: `args.get('num_results', 5)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:437
  - 代码: `args.get('num_results', 5)`
  - 建议: 使用 aiohttp

- **session.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:466
  - 代码: `session.get(f'{KIMI_API_BASE}/models', headers=headers, timeout=10)`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:474
  - 代码: `m.get('id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:474
  - 代码: `data.get('data', [])`
  - 建议: 使用 aiohttp

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:493
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:499
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:507
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:303
  - 代码: `args.get('confidence', 0.25)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:304
  - 代码: `args.get('save_result', True)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:366
  - 代码: `args.get('confidence', 0.3)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:367
  - 代码: `args.get('save_result', True)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:425
  - 代码: `args.get('confidence', 0.25)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:426
  - 代码: `args.get('save_result', True)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:484
  - 代码: `args.get('task', 'all')`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:485
  - 代码: `args.get('confidence', 0.25)`
  - 建议: 使用 aiohttp

- **args.get**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:634
  - 代码: `args.get('dataset_name', 'flood_sample')`
  - 建议: 使用 aiohttp

- **cv2.imwrite**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:665
  - 代码: `cv2.imwrite(img_path, img)`
  - 建议: 使用异步写入方法

- **platform.system**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:697
  - 代码: `platform.system()`
  - 建议: 使用 asyncio.create_subprocess_exec

- **server.run**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:705
  - 代码: `server.run(read_stream, write_stream, server.create_initialization_options())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:713
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:71
  - 代码: `config.get('key')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:72
  - 代码: `config.get('default')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:73
  - 代码: `data_pool.get(key, default)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:154
  - 代码: `config.get('operation')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:155
  - 代码: `config.get('a', 0)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:156
  - 代码: `config.get('b', 0)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:199
  - 代码: `config.get('data_key')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:200
  - 代码: `data_pool.get(data_key)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:208
  - 代码: `config.get('columns', df.columns.tolist())`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:243
  - 代码: `config.get('data_key')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:244
  - 代码: `config.get('indent', 2)`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:245
  - 代码: `data_pool.get(data_key)`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:288
  - 代码: `config.get('timestamp')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:289
  - 代码: `config.get('format', '%Y-%m-%d %H:%M:%S')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:331
  - 代码: `config.get('level', 'info')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:332
  - 代码: `config.get('message', '')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:333
  - 代码: `config.get('context', {})`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:372
  - 代码: `config.get('title', '执行报告')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:373
  - 代码: `config.get('metrics', {})`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\common_tools.py:374
  - 代码: `config.get('results', {})`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:162
  - 代码: `config.get('station', '未知站点')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:163
  - 代码: `config.get('data_type', '水位')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:192
  - 代码: `config.get('process_type', '统计分析')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:218
  - 代码: `config.get('forecast_type', '水位预报')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:219
  - 代码: `config.get('horizon', '24小时')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:252
  - 代码: `config.get('calc_type', '洪水频率分析')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:283
  - 代码: `config.get('sim_type', '洪水演进')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:312
  - 代码: `config.get('opt_type', '水库群联合优化')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:345
  - 代码: `config.get('decision_type', '调度决策')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:375
  - 代码: `config.get('action', '调整出库流量')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:380
  - 代码: `config.get('target', '三峡大坝')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:381
  - 代码: `config.get('value', round(random.uniform(15000.0, 25000.0), 0))`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:398
  - 代码: `config.get('check_type', '方案可行性检查')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:422
  - 代码: `config.get('report_type', '调度分析报告')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:462
  - 代码: `config.get('question', '')`
  - 建议: 使用 aiohttp

- **data_pool.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:465
  - 代码: `data_pool.get('raw_user_input', '请回答一个通用问题')`
  - 建议: 使用 aiohttp

- **config.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:468
  - 代码: `config.get('task_context', {})`
  - 建议: 使用 aiohttp

- **task_context.get**
  - 位置: src\flood_decision_agent\tools\execution_tools.py:469
  - 代码: `task_context.get('task_type', 'general')`
  - 建议: 使用 aiohttp

- **self._tools.get**
  - 位置: src\flood_decision_agent\tools\llm_tools.py:166
  - 代码: `self._tools.get(name)`
  - 建议: 使用 aiohttp

- **self._official_tools.get**
  - 位置: src\flood_decision_agent\tools\llm_tools.py:181
  - 代码: `self._official_tools.get(name)`
  - 建议: 使用 aiohttp

- **self._tools.get**
  - 位置: src\flood_decision_agent\tools\registry.py:107
  - 代码: `self._tools.get(name)`
  - 建议: 使用 aiohttp

- **self._metadata.get**
  - 位置: src\flood_decision_agent\tools\registry.py:111
  - 代码: `self._metadata.get(name)`
  - 建议: 使用 aiohttp

- **meta.config_schema.get**
  - 位置: src\flood_decision_agent\tools\registry.py:137
  - 代码: `meta.config_schema.get('required', [])`
  - 建议: 使用 aiohttp

- **self.get**
  - 位置: src\flood_decision_agent\tools\registry.py:153
  - 代码: `self.get(name)`
  - 建议: 使用 aiohttp

- **status_map.get**
  - 位置: src\flood_decision_agent\visualization\base.py:234
  - 代码: `status_map.get(node.status.value, TaskStatus.PENDING)`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: src\flood_decision_agent\visualization\base.py:302
  - 代码: `self._task_info_map.get(node_id)`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: src\flood_decision_agent\visualization\base.py:340
  - 代码: `self._task_info_map.get(node_id)`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: src\flood_decision_agent\visualization\base.py:382
  - 代码: `self._task_info_map.get(node_id)`
  - 建议: 使用 aiohttp

- **self._render_agent_call**
  - 位置: src\flood_decision_agent\visualization\base.py:434
  - 代码: `self._render_agent_call(agent_call)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **ascii_map.get**
  - 位置: src\flood_decision_agent\visualization\terminal.py:187
  - 代码: `ascii_map.get(name, '')`
  - 建议: 使用 aiohttp

- **self.ICONS.get**
  - 位置: src\flood_decision_agent\visualization\terminal.py:188
  - 代码: `self.ICONS.get(name, '')`
  - 建议: 使用 aiohttp

- **icon_map.get**
  - 位置: src\flood_decision_agent\visualization\terminal.py:269
  - 代码: `icon_map.get(status, ('pending', TerminalColors.DIM))`
  - 建议: 使用 aiohttp

- **text_map.get**
  - 位置: src\flood_decision_agent\visualization\terminal.py:289
  - 代码: `text_map.get(status, ('未知', TerminalColors.DIM))`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:86
  - 代码: `client.get('/api/health')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:102
  - 代码: `client.post('/api/conversations', json={'title': '测试对话'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:110
  - 代码: `client.get('/api/conversations')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:118
  - 代码: `client.get(f'/api/conversations/{conv_id}')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:125
  - 代码: `client.get('/api/conversations/non_existent_id')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:130
  - 代码: `client.post(f'/api/conversations/{conv_id}/clear')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:154
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:158
  - 代码: `client.post('/api/chat', json={'message': '你好', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:170
  - 代码: `client.post('/api/chat', json={'message': '计算1+1', 'conversation_id': conv_id, 'stream': True})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:186
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:195
  - 代码: `client.get(f'/api/conversations/{conv_id}/messages')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:202
  - 代码: `client.get(f'/api/conversations/{conv_id}/process-events')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:227
  - 代码: `client.post('/api/mode/detect', json={'user_input': user_input})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:245
  - 代码: `client.post('/data/parse', json={'input_data': '河道名称: 示例河, 断面桩号: K0+100', 'input_type': 'text', 'schema_type': 'river_cross_section'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:258
  - 代码: `client.post('/data/request', json={'data_key': 'roughness_coefficient', 'description': '河道糙率系数', 'required': True, 'context': {'river_type': '山区河道'}})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:268
  - 代码: `client.get('/data/defaults?data_key=roughness_coefficient')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:273
  - 代码: `client.post('/data/confirm', json={'confirmation_id': 'conf_test_001', 'status': 'confirmed', 'modified_data': None, 'user_notes': ''})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:283
  - 代码: `client.get('/data/lineage/test_key')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:288
  - 代码: `client.post('/data/clarification/session', json={'task_id': 'task_test_001', 'data_dependencies': [{'data_key': 'river_width', 'description': '河道宽度', 'required': True}]})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:298
  - 代码: `client.post('/data/clarification/resolve', json={'session_id': 'session_test_001', 'request_id': 'req_test_001', 'resolution_type': 'default', 'value': None})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:317
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '设计一个洪水预警系统，包含数据采集、预警模型、通知机制等模块'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:324
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:337
  - 代码: `client.post(f'/api/plans/{plan_id}/modify', json={'instruction': '把准确率目标改成98%，增加应急预案章节'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:343
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:347
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:353
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:357
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:371
  - 代码: `client.post('/api/plans/non_existent_plan/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:379
  - 代码: `client.post(f'/api/plans/{plan_id_2}/generate', json={'user_input': '另一个规划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:384
  - 代码: `client.post(f'/api/plans/{plan_id_2}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:390
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:394
  - 代码: `client.post('/api/plans/non_existent_plan/cancel', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:408
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '设计洪水预警系统的技术规格，包括API接口、数据模型、业务逻辑'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:415
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:428
  - 代码: `client.post(f'/api/specs/{feature_name}/modify', json={'instruction': '增加缓存设计章节，优化数据库表结构'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:434
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:438
  - 代码: `client.post(f'/api/specs/{feature_name}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:444
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:454
  - 代码: `client.post('/api/specs/non_existent_spec/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:462
  - 代码: `client.post(f'/api/specs/{feature_name_2}/generate', json={'user_input': '另一个规格'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:467
  - 代码: `client.post(f'/api/specs/{feature_name_2}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:473
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:477
  - 代码: `client.post('/api/specs/non_existent_spec/cancel', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:489
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:518
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\comprehensive_api_test.py:519
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:540
  - 代码: `client.post('/api/conversations', json={'title': 'E2E测试对话'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:544
  - 代码: `client.post('/api/mode/detect', json={'user_input': '计算河道流量'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:551
  - 代码: `client.post('/api/chat', json={'message': '你好，请介绍一下洪水预警系统', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:561
  - 代码: `client.get(f'/api/conversations/{conv_id}/messages')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\comprehensive_api_test.py:566
  - 代码: `client.get(f'/api/conversations/{conv_id}/process-events')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:580
  - 代码: `client.post('/api/conversations', json={'title': 'Plan模式测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:584
  - 代码: `client.post('/api/mode/detect', json={'user_input': '制定一个洪水预警系统开发计划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:592
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '制定洪水预警系统开发计划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:604
  - 代码: `client.post(f'/api/plans/{plan_id}/modify', json={'instruction': '把准确率目标改成98%'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:610
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:626
  - 代码: `client.post('/api/conversations', json={'title': 'Spec模式测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:630
  - 代码: `client.post('/api/mode/detect', json={'user_input': '编写洪水预警系统API规格文档'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:638
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '编写洪水预警系统API规格文档'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:650
  - 代码: `client.post(f'/api/specs/{feature_name}/modify', json={'instruction': '增加认证相关的接口定义'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\comprehensive_api_test.py:656
  - 代码: `client.post(f'/api/specs/{feature_name}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:35
  - 代码: `client.get('/api/health')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:49
  - 代码: `client.get('/api/conversations')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:54
  - 代码: `client.post('/api/conversations', json={'title': '测试对话'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:60
  - 代码: `client.get(f'/api/conversations/{conv_id}')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:65
  - 代码: `client.get(f'/api/conversations/{conv_id}/messages')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:70
  - 代码: `client.get(f'/api/conversations/{conv_id}/process-events')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:75
  - 代码: `client.post(f'/api/conversations/{conv_id}/clear')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:94
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:98
  - 代码: `client.post('/api/chat', json={'message': '你好', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:115
  - 代码: `client.post('/api/mode/detect', json={'user_input': '设计一个洪水预警系统'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\test_all_apis.py:120
  - 代码: `data.get('recommended_mode')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:133
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '设计一个洪水预警系统'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:154
  - 代码: `client.post(f'/api/plans/{plan_id}/modify', json={'instruction': '把准确率目标改成98%'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:165
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:177
  - 代码: `client.post(f'/api/plans/{plan_id_2}/generate', json={'user_input': '测试取消'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:178
  - 代码: `client.post(f'/api/plans/{plan_id_2}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:204
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '实现洪水预警模块'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:225
  - 代码: `client.post(f'/api/specs/{feature_name}/modify', json={'instruction': '添加性能要求：响应时间小于1秒'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:236
  - 代码: `client.post(f'/api/specs/{feature_name}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:248
  - 代码: `client.post(f'/api/specs/{feature_name_2}/generate', json={'user_input': '测试取消'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:249
  - 代码: `client.post(f'/api/specs/{feature_name_2}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:272
  - 代码: `client.post('/data/parse', json={'input_data': '河道宽度: 100m, 深度: 5m', 'input_type': 'text', 'schema_type': 'river_cross_section'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_all_apis.py:281
  - 代码: `client.post('/data/request', json={'data_key': 'roughness_coefficient', 'description': '河道糙率系数', 'required': True})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_all_apis.py:291
  - 代码: `client.get('/data/defaults?data_key=roughness_coefficient')`
  - 建议: 使用 aiohttp

- **requests.get**
  - 位置: tests\test_chain_generation_api.py:30
  - 代码: `requests.get(f'{base_url}/api/health')`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:37
  - 代码: `requests.post(f'{base_url}/api/chain-generation/generate', json={'user_input': '设计一个洪水预警系统，能够实时监测水位并发送预警通知', 'conversation_id': 'test_conv_001'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:53
  - 代码: `requests.post(f'{base_url}/api/chain-generation/generate', json={'user_input': '', 'conversation_id': 'test_conv_001'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:66
  - 代码: `requests.post(f'{base_url}/api/chain-generation/generate-from-plan', json={'plan_id': 'non_existent_plan', 'conversation_id': 'test_conv_001'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:81
  - 代码: `requests.post(storage_url, json={'user_input': '测试规划'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:87
  - 代码: `requests.post(f'{base_url}/api/chain-generation/generate-from-plan', json={'plan_id': 'test_plan_unconfirmed', 'conversation_id': 'test_conv_001'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:99
  - 代码: `requests.post(f'{base_url}/api/chain-generation/generate-from-spec', json={'feature_name': 'non_existent_spec', 'conversation_id': 'test_conv_001'})`
  - 建议: 使用 aiohttp

- **requests.get**
  - 位置: tests\test_chain_generation_api.py:112
  - 代码: `requests.get(f'{base_url}/api/chain-generation/non_existent/status')`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:121
  - 代码: `requests.post(f'{base_url}/api/chain-generation/non_existent/execute', json={'generation_id': 'non_existent', 'mode': 'normal', 'auto_execute': True})`
  - 建议: 使用 aiohttp

- **requests.get**
  - 位置: tests\test_chain_generation_api.py:135
  - 代码: `requests.get(f'{base_url}/api/chain-generation/executions/non_existent/status')`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: tests\test_chain_generation_api.py:144
  - 代码: `requests.post(f'{base_url}/api/chain-generation/executions/non_existent/cancel')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\test_chain_generation_api.py:215
  - 代码: `data.get('message')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:24
  - 代码: `client.post('/api/sessions', json={'conversation_id': 'test_conv_001', 'mode': 'plan'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:35
  - 代码: `client.get(f'/api/sessions/{session_id}/status')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:43
  - 代码: `client.post(f'/api/sessions/{session_id}/update', json={'status': 'awaiting_confirmation', 'can_resume': True, 'current_document': {'type': 'plan', 'id': 'plan_001', 'title': '测试规划', 'status': 'draft'}})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:60
  - 代码: `client.post(f'/api/sessions/{session_id}/resume')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:68
  - 代码: `client.post('/api/sessions/resume', json={'session_id': session_id})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:77
  - 代码: `client.get('/api/sessions/non_existent/status')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:82
  - 代码: `client.get('/api/sessions')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:99
  - 代码: `client.post('/api/specs', json={'user_input': '测试规格'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:108
  - 代码: `client.get('/api/specs')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:115
  - 代码: `client.get(f'/api/specs/{feature_name}')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:123
  - 代码: `client.get(f'/api/specs/{feature_name}/files')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:131
  - 代码: `client.get(f'/api/specs/{feature_name}/spec')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_frontend_apis.py:139
  - 代码: `client.get(f'/api/specs/{feature_name}/spec.md')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:155
  - 代码: `client.post(f'/api/specs/{feature_name}/approve')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_frontend_apis.py:166
  - 代码: `client.post('/api/mode/detect', json={'user_input': '制定一个洪水预警计划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:24
  - 代码: `client.post('/api/conversations', json={'title': 'Plan测试对话'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:33
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': f'测试规划 {i + 1}'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:41
  - 代码: `client.get(f'/api/conversations/{conv_id}/plans')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:50
  - 代码: `client.get(f'/api/conversations/{conv_id}/plans?status=draft')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:56
  - 代码: `client.get(f'/api/conversations/{conv_id}/plans?page=1&page_size=2')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:63
  - 代码: `client.get('/api/conversations/non_existent/plans')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:77
  - 代码: `client.post('/api/conversations', json={'title': 'Spec测试对话'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:86
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': f'测试规格 {i + 1}'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:94
  - 代码: `client.get(f'/api/conversations/{conv_id}/specs')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:103
  - 代码: `client.get(f'/api/conversations/{conv_id}/specs?status=draft')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:109
  - 代码: `client.get(f'/api/conversations/{conv_id}/specs?page=1&page_size=2')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:116
  - 代码: `client.get('/api/conversations/non_existent/specs')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:130
  - 代码: `client.post('/api/conversations', json={'title': '结构测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:133
  - 代码: `client.post('/api/plans/plan_struct_test/generate', json={'user_input': '测试'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:136
  - 代码: `client.get(f'/api/conversations/{conv_id}/plans')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\test_new_apis.py:165
  - 代码: `client.post('/api/specs/spec_struct_test/generate', json={'user_input': '测试'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\test_new_apis.py:167
  - 代码: `client.get(f'/api/conversations/{conv_id}/specs')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\test_websocket_live.py:39
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\test_websocket_live.py:40
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\test_websocket_live.py:49
  - 代码: `asyncio.run(test_websocket())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **message.payload.get**
  - 位置: tests\agents\test_base_agent.py:11
  - 代码: `message.payload.get('data')`
  - 建议: 使用 aiohttp

- **intent.goal.get**
  - 位置: tests\agents\test_decision_chain_generator.py:71
  - 代码: `intent.goal.get('outflow')`
  - 建议: 使用 aiohttp

- **intent.constraints.get**
  - 位置: tests\agents\test_decision_chain_generator.py:72
  - 代码: `intent.constraints.get('max_rate')`
  - 建议: 使用 aiohttp

- **sample_task_graph.get_ready_nodes**
  - 位置: tests\agents\test_node_scheduler.py:138
  - 代码: `sample_task_graph.get_ready_nodes()`
  - 建议: 使用异步读取方法

- **sample_task_graph.get_ready_nodes**
  - 位置: tests\agents\test_node_scheduler.py:147
  - 代码: `sample_task_graph.get_ready_nodes()`
  - 建议: 使用异步读取方法

- **sample_task_graph.get_ready_nodes**
  - 位置: tests\agents\test_node_scheduler.py:155
  - 代码: `sample_task_graph.get_ready_nodes()`
  - 建议: 使用异步读取方法

- **scheduler_agent.run**
  - 位置: tests\agents\test_node_scheduler.py:532
  - 代码: `scheduler_agent.run(sample_task_graph, data_pool)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **.metadata.get**
  - 位置: tests\agents\test_task_decomposer.py:324
  - 代码: `task_nodes[0].metadata.get('priority')`
  - 建议: 使用 aiohttp

- **t.get**
  - 位置: tests\core\test_chain_optimizer.py:351
  - 代码: `t.get('priority', 100)`
  - 建议: 使用 aiohttp

- **critical_node.metadata.get**
  - 位置: tests\core\test_heuristic_optimizer.py:304
  - 代码: `critical_node.metadata.get('critical_path')`
  - 建议: 使用 aiohttp

- **critical_node.metadata.get**
  - 位置: tests\core\test_heuristic_optimizer.py:305
  - 代码: `critical_node.metadata.get('priority')`
  - 建议: 使用 aiohttp

- **critical_node.metadata.get**
  - 位置: tests\core\test_heuristic_optimizer.py:306
  - 代码: `critical_node.metadata.get('retry_enabled')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:37
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:42
  - 代码: `data.get('intent', {})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:44
  - 代码: `data.get('stage')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:44
  - 代码: `data.get('progress')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:46
  - 代码: `data.get('total_count')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:48
  - 代码: `data.get('generation_id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:50
  - 代码: `data.get('execution_id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:50
  - 代码: `data.get('total_tasks')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:52
  - 代码: `data.get('task_id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:52
  - 代码: `data.get('status')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:54
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:56
  - 代码: `data.get('content', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_detailed_websocket.py:59
  - 代码: `data.get('message')`
  - 建议: 使用 aiohttp

- **msg.get**
  - 位置: tests\e2e\test_detailed_websocket.py:69
  - 代码: `msg.get('type')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\e2e\test_detailed_websocket.py:73
  - 代码: `asyncio.run(test_chat_detailed())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **data.get**
  - 位置: tests\e2e\test_simple_websocket.py:34
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_simple_websocket.py:36
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_simple_websocket.py:37
  - 代码: `data.get('message')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_simple_websocket.py:39
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_simple_websocket.py:40
  - 代码: `data.get('content')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\e2e\test_simple_websocket.py:50
  - 代码: `asyncio.run(test_chat())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:29
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:50
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:81
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:84
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\e2e\test_websocket_e2e.py:91
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\e2e\test_websocket_e2e.py:96
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:130
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:132
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:133
  - 代码: `data.get('document_id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:136
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\e2e\test_websocket_e2e.py:143
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:162
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:164
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\e2e\test_websocket_e2e.py:170
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\e2e\test_websocket_e2e.py:211
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\e2e\test_websocket_e2e.py:217
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\e2e\test_websocket_e2e.py:272
  - 代码: `asyncio.run(run_all_tests())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **metrics.record_tool_call**
  - 位置: tests\evaluation\test_metrics.py:148
  - 代码: `metrics.record_tool_call('tool1', success=True)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **metrics.record_tool_call**
  - 位置: tests\evaluation\test_metrics.py:149
  - 代码: `metrics.record_tool_call('tool2', success=False)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **metrics.record_tool_call**
  - 位置: tests\evaluation\test_metrics.py:150
  - 代码: `metrics.record_tool_call('tool3', success=True)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **pipeline.run**
  - 位置: tests\integration\test_advanced_pipeline.py:96
  - 代码: `pipeline.run(user_input)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **pipeline.run**
  - 位置: tests\integration\test_advanced_pipeline.py:127
  - 代码: `pipeline.run(user_input)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **node.get**
  - 位置: tests\integration\test_advanced_pipeline.py:138
  - 代码: `node.get('node_id')`
  - 建议: 使用 aiohttp

- **node.get**
  - 位置: tests\integration\test_advanced_pipeline.py:138
  - 代码: `node.get('task_type')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: tests\integration\test_advanced_pipeline.py:196
  - 代码: `pipeline.run(user_input)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **node.get**
  - 位置: tests\integration\test_advanced_pipeline.py:207
  - 代码: `node.get('node_id')`
  - 建议: 使用 aiohttp

- **node.get**
  - 位置: tests\integration\test_advanced_pipeline.py:207
  - 代码: `node.get('task_type')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\integration\test_advanced_pipeline.py:243
  - 代码: `asyncio.run(setup())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\integration\test_advanced_pipeline.py:265
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\integration\test_advanced_pipeline.py:267
  - 代码: `result.get('result', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\integration\test_advanced_pipeline.py:269
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\integration\test_advanced_pipeline.py:275
  - 代码: `asyncio.run(execute())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\integration\test_advanced_pipeline.py:290
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\integration\test_advanced_pipeline.py:327
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\integration\test_api_complete_validation.py:25
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_api_complete_validation.py:74
  - 代码: `open(plan_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_api_complete_validation.py:75
  - 代码: `f.write(plan_result['plan_document'])`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_api_complete_validation.py:103
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\integration\test_api_complete_validation.py:139
  - 代码: `result.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_api_complete_validation.py:157
  - 代码: `open(plan_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_api_complete_validation.py:158
  - 代码: `f.write(result['plan_result']['plan_document'])`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\integration\test_api_complete_validation.py:163
  - 代码: `open(spec_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_api_complete_validation.py:164
  - 代码: `f.write(result['spec_result']['spec_document'])`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\integration\test_api_complete_validation.py:170
  - 代码: `open(tasks_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_api_complete_validation.py:171
  - 代码: `f.write(result['tasks_result']['tasks_document'])`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\integration\test_api_complete_validation.py:177
  - 代码: `open(checklist_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_api_complete_validation.py:178
  - 代码: `f.write(result['checklist_result']['checklist_document'])`
  - 建议: 使用异步写入方法

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:28
  - 代码: `client.get('/api/health')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:42
  - 代码: `client.post('/api/conversations', json={'title': '测试对话'})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:49
  - 代码: `client.get('/api/conversations')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:56
  - 代码: `client.get(f'/api/conversations/{conv_id}')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:62
  - 代码: `client.get('/api/conversations/non_existent_id')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:66
  - 代码: `client.post(f'/api/conversations/{conv_id}/clear')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:86
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:90
  - 代码: `client.post('/api/chat', json={'message': '你好', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:106
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:110
  - 代码: `client.post('/api/chat', json={'message': '计算1+1', 'conversation_id': conv_id, 'stream': True})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:126
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:139
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:143
  - 代码: `client.post('/api/chat', json={'message': '你好', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:150
  - 代码: `client.get(f'/api/conversations/{conv_id}/messages')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:156
  - 代码: `client.get(f'/api/conversations/{conv_id}/process-events')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:179
  - 代码: `client.post('/api/mode/detect', json={'user_input': user_input})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:193
  - 代码: `client.post('/data/parse', json={'input_data': '河道名称: 示例河, 断面桩号: K0+100', 'input_type': 'text', 'schema_type': 'river_cross_section'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:202
  - 代码: `client.post('/data/request', json={'data_key': 'roughness_coefficient', 'description': '河道糙率系数', 'required': True, 'context': {'river_type': '山区河道'}})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:212
  - 代码: `client.get('/data/defaults?data_key=roughness_coefficient')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:217
  - 代码: `client.post('/data/confirm', json={'confirmation_id': 'conf_test_001', 'status': 'confirmed', 'modified_data': None, 'user_notes': ''})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:227
  - 代码: `client.get('/data/lineage/test_key')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:232
  - 代码: `client.post('/data/clarification/session', json={'task_id': 'task_test_001', 'data_dependencies': [{'data_key': 'river_width', 'description': '河道宽度', 'required': True}]})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:242
  - 代码: `client.post('/data/clarification/resolve', json={'session_id': 'session_test_001', 'request_id': 'req_test_001', 'resolution_type': 'default', 'value': None})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:259
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '设计一个洪水预警系统'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:276
  - 代码: `client.post(f'/api/plans/{plan_id}/modify', json={'instruction': '把准确率目标改成98%'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:284
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:290
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:301
  - 代码: `client.post('/api/plans/non_existent_plan/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:307
  - 代码: `client.post('/api/plans/non_existent_plan/cancel', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:315
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '测试规划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:320
  - 代码: `client.post(f'/api/plans/{plan_id}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:326
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:337
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '设计洪水预警系统的技术规格'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:354
  - 代码: `client.post(f'/api/specs/{feature_name}/modify', json={'instruction': '增加缓存设计章节'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:362
  - 代码: `client.post(f'/api/specs/{feature_name}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:368
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:379
  - 代码: `client.post('/api/specs/non_existent_spec/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:385
  - 代码: `client.post('/api/specs/non_existent_spec/cancel', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:393
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '测试规格'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:398
  - 代码: `client.post(f'/api/specs/{feature_name}/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:404
  - 代码: `data.get('data', {})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:413
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:434
  - 代码: `client.post('/api/conversations', json={})`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:453
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_api_comprehensive.py:454
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:471
  - 代码: `client.post('/api/conversations', json={'title': 'E2E测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:476
  - 代码: `client.post('/api/mode/detect', json={'user_input': '计算河道流量'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:482
  - 代码: `client.post('/api/chat', json={'message': '你好', 'conversation_id': conv_id, 'stream': False})`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:490
  - 代码: `client.get(f'/api/conversations/{conv_id}/messages')`
  - 建议: 使用 aiohttp

- **client.get**
  - 位置: tests\integration\test_api_comprehensive.py:495
  - 代码: `client.get(f'/api/conversations/{conv_id}/process-events')`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:504
  - 代码: `client.post('/api/conversations', json={'title': 'Plan测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:509
  - 代码: `client.post('/api/mode/detect', json={'user_input': '制定洪水预警系统开发计划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:516
  - 代码: `client.post(f'/api/plans/{plan_id}/generate', json={'user_input': '制定洪水预警系统开发计划'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:528
  - 代码: `client.post(f'/api/plans/{plan_id}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:539
  - 代码: `client.post('/api/conversations', json={'title': 'Spec测试'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:544
  - 代码: `client.post('/api/mode/detect', json={'user_input': '编写API规格文档'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:551
  - 代码: `client.post(f'/api/specs/{feature_name}/generate', json={'user_input': '编写API规格文档'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\integration\test_api_comprehensive.py:563
  - 代码: `client.post(f'/api/specs/{feature_name}/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_direct_api.py:7
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_kimi_api_simple.py:11
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_unified_optimizer.py:95
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_unified_optimizer.py:157
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_unified_optimizer.py:229
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_unified_optimizer.py:351
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **result.execution_summary.get**
  - 位置: tests\integration\test_visualization_integration.py:201
  - 代码: `result.execution_summary.get('total_tasks')`
  - 建议: 使用 aiohttp

- **result.execution_summary.get**
  - 位置: tests\integration\test_visualization_integration.py:202
  - 代码: `result.execution_summary.get('completed_tasks')`
  - 建议: 使用 aiohttp

- **result.execution_summary.get**
  - 位置: tests\integration\test_visualization_integration.py:203
  - 代码: `result.execution_summary.get('failed_tasks')`
  - 建议: 使用 aiohttp

- **result.execution_summary.get**
  - 位置: tests\integration\test_visualization_integration.py:204
  - 代码: `result.execution_summary.get('total_duration_ms', 0)`
  - 建议: 使用 aiohttp

- **runner.run**
  - 位置: tests\integration\test_visualization_integration.py:431
  - 代码: `runner.run(suite)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **metadata.get**
  - 位置: tests\integration\test_water_plan_chain_integration.py:249
  - 代码: `metadata.get('reliability_score', 0)`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_chain_integration.py:284
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **.environ.get**
  - 位置: tests\integration\test_water_plan_chain_integration.py:287
  - 代码: `__import__('os').environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **runner.run**
  - 位置: tests\integration\test_water_plan_chain_integration.py:332
  - 代码: `runner.run(suite)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_single.py:18
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_plan_single.py:68
  - 代码: `open(output_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_plan_single.py:69
  - 代码: `f.write(result['plan_document'])`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:26
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_plan_with_api.py:82
  - 代码: `open(output_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_plan_with_api.py:83
  - 代码: `f.write(result['plan_document'])`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:42
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_plan_with_api.py:139
  - 代码: `open(output_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_plan_with_api.py:140
  - 代码: `f.write(result['plan_document'])`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:101
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:158
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_plan_with_api.py:259
  - 代码: `open(plan_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_plan_with_api.py:260
  - 代码: `f.write(result['plan_result']['plan_document'])`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:206
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:266
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_plan_with_api.py:344
  - 代码: `open(output_dir / 'plan_with_domain_knowledge.md', 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_plan_with_api.py:345
  - 代码: `f.write(plan_with)`
  - 建议: 使用异步写入方法

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:310
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\integration\test_water_plan_with_api.py:357
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **runner.run**
  - 位置: tests\integration\test_water_plan_with_api.py:388
  - 代码: `runner.run(suite)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\integration\test_water_spec_with_api.py:23
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\integration\test_water_spec_with_api.py:64
  - 代码: `result.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\integration\test_water_spec_with_api.py:79
  - 代码: `open(plan_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_spec_with_api.py:80
  - 代码: `f.write(result['plan_result']['plan_document'])`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\integration\test_water_spec_with_api.py:85
  - 代码: `open(spec_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\integration\test_water_spec_with_api.py:86
  - 代码: `f.write(result['spec_result']['spec_document'])`
  - 建议: 使用异步写入方法

- **asyncio.sleep**
  - 位置: tests\integration\test_websocket_chain_generation.py:42
  - 代码: `asyncio.sleep(0.1)`
  - 建议: 使用 asyncio.sleep

- **m.get**
  - 位置: tests\integration\test_websocket_chain_generation.py:177
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\integration\test_websocket_chain_generation.py:241
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: tests\integration\test_websocket_chain_generation.py:468
  - 代码: `asyncio.sleep(0.1)`
  - 建议: 使用 asyncio.sleep

- **m.get**
  - 位置: tests\integration\test_websocket_chain_generation.py:474
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: tests\integration\test_websocket_chain_generation.py:493
  - 代码: `asyncio.sleep(0.1)`
  - 建议: 使用 asyncio.sleep

- **m.get**
  - 位置: tests\integration\test_websocket_chain_generation.py:499
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_websocket_integration.py:71
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\integration\test_websocket_integration.py:77
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: tests\integration\test_websocket_integration.py:98
  - 代码: `kwargs.get('on_chunk')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_websocket_integration.py:123
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\integration\test_websocket_integration.py:129
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **kwargs.get**
  - 位置: tests\integration\test_websocket_integration.py:150
  - 代码: `kwargs.get('on_chunk')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\integration\test_websocket_integration.py:175
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **m.get**
  - 位置: tests\integration\test_websocket_integration.py:181
  - 代码: `m.get('type')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:68
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:70
  - 代码: `result.get('providers', {})`
  - 建议: 使用 aiohttp

- **status.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:72
  - 代码: `status.get('available')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:75
  - 代码: `result.get('warning', '未知状态')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:84
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:85
  - 代码: `result.get('count', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:87
  - 代码: `result.get('message', '无数据')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:98
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:99
  - 代码: `result.get('entries', [])`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:102
  - 代码: `result.get('error', '无数据')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: tests\mcp\start_all_mcp_servers.py:123
  - 代码: `asyncio.sleep(1)`
  - 建议: 使用 asyncio.sleep

- **os.environ.get**
  - 位置: tests\mcp\start_all_mcp_servers.py:132
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\start_all_mcp_servers.py:137
  - 代码: `asyncio.run(start_and_test_all_servers())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:71
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:72
  - 代码: `result.get('providers', {})`
  - 建议: 使用 aiohttp

- **s.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:73
  - 代码: `s.get('available')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:76
  - 代码: `result.get('warning', '未配置')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:85
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:86
  - 代码: `result.get('count', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:97
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:98
  - 代码: `result.get('entries', [])`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:127
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:128
  - 代码: `result.get('device', 'unknown')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\mcp\test_all_mcp_servers.py:154
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_all_mcp_servers.py:158
  - 代码: `asyncio.run(test_all_servers())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **response.payload.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:74
  - 代码: `response.payload.get('task_graph')`
  - 建议: 使用 aiohttp

- **response.payload.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:75
  - 代码: `response.payload.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:79
  - 代码: `metadata.get('mode', 'unknown')`
  - 建议: 使用 aiohttp

- **node_metadata.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:89
  - 代码: `node_metadata.get('mcp_tools', [])`
  - 建议: 使用 aiohttp

- **concurrent.futures.ThreadPoolExecutor**
  - 位置: tests\mcp\test_decision_chain_mcp.py:116
  - 代码: `concurrent.futures.ThreadPoolExecutor()`
  - 建议: 使用异步读取方法

- **asyncio.run**
  - 位置: tests\mcp\test_decision_chain_mcp.py:121
  - 代码: `asyncio.run(agent.initialize_mcp())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **tool_info.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:131
  - 代码: `tool_info.get('server_name', 'unknown')`
  - 建议: 使用 aiohttp

- **concurrent.futures.ThreadPoolExecutor**
  - 位置: tests\mcp\test_decision_chain_mcp.py:156
  - 代码: `concurrent.futures.ThreadPoolExecutor()`
  - 建议: 使用异步读取方法

- **asyncio.run**
  - 位置: tests\mcp\test_decision_chain_mcp.py:160
  - 代码: `asyncio.run(agent.initialize_mcp())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\mcp\test_decision_chain_mcp.py:195
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **tool_info.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:45
  - 代码: `tool_info.get('server_name', 'unknown')`
  - 建议: 使用 aiohttp

- **first_tool_info.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:144
  - 代码: `first_tool_info.get('server_name', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:162
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:164
  - 代码: `result.get('data', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:166
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:200
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:201
  - 代码: `result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:202
  - 代码: `result.get('metrics', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:205
  - 代码: `result.get('status')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:206
  - 代码: `result.get('output', {})`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\mcp\test_mcp_auto_select.py:269
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_auto_select.py:276
  - 代码: `asyncio.run(test_mcp_manager_directly())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_auto_select.py:279
  - 代码: `asyncio.run(test_mcp_initialization())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_auto_select.py:285
  - 代码: `asyncio.run(test_mcp_tool_execution(executor))`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_auto_select.py:295
  - 代码: `asyncio.run(executor._mcp_manager.close_all())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:66
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:67
  - 代码: `result.get('message')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:68
  - 代码: `result.get('filepath')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:70
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:71
  - 代码: `result.get('error', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:92
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:94
  - 代码: `result.get('input_file')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:95
  - 代码: `result.get('output_file')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:96
  - 代码: `result.get('paragraphs')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:97
  - 代码: `result.get('tables')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:100
  - 代码: `result.get('content_preview', '')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_document.py:107
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **result1.get**
  - 位置: tests\mcp\test_mcp_document.py:157
  - 代码: `result1.get('success')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_document.py:168
  - 代码: `result2.get('success')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_document.py:170
  - 代码: `result2.get('success')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_document.py:171
  - 代码: `result2.get('output_file')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_document.py:172
  - 代码: `result2.get('output_path')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_document.py:205
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:76
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:78
  - 代码: `result.get('result', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:80
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:175
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:177
  - 代码: `result.get('result')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_executor_integration.py:179
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_executor_integration.py:264
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:83
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result1.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:107
  - 代码: `result1.get('success')`
  - 建议: 使用 aiohttp

- **result1.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:108
  - 代码: `result1.get('filepath')`
  - 建议: 使用 aiohttp

- **result1.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:110
  - 代码: `result1.get('error')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:125
  - 代码: `result2.get('success')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:126
  - 代码: `result2.get('output_file')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:127
  - 代码: `result2.get('paragraphs')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:128
  - 代码: `result2.get('tables')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:130
  - 代码: `result2.get('error')`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:148
  - 代码: `result3.get('success')`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:149
  - 代码: `result3.get('outputs', {})`
  - 建议: 使用 aiohttp

- **outputs.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:151
  - 代码: `outputs.get('total_runoff', 0)`
  - 建议: 使用 aiohttp

- **outputs.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:152
  - 代码: `outputs.get('peak_discharge', 0)`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:157
  - 代码: `result3.get('error')`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:163
  - 代码: `result3.get('outputs', {})`
  - 建议: 使用 aiohttp

- **result4.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:176
  - 代码: `result4.get('success')`
  - 建议: 使用 aiohttp

- **result4.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:177
  - 代码: `result4.get('outputs', {})`
  - 建议: 使用 aiohttp

- **outputs.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:179
  - 代码: `outputs.get('peak_attenuation', 0)`
  - 建议: 使用 aiohttp

- **result4.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:181
  - 代码: `result4.get('error')`
  - 建议: 使用 aiohttp

- **result4.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:187
  - 代码: `result4.get('outputs', {})`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:207
  - 代码: `result5.get('success')`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:208
  - 代码: `result5.get('plan', {})`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:210
  - 代码: `plan.get('plan_id')`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:211
  - 代码: `plan.get('time_steps')`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:212
  - 代码: `plan.get('total_release', 0)`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:214
  - 代码: `result5.get('error')`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:230
  - 代码: `result3.get('outputs', {})`
  - 建议: 使用 aiohttp

- **result3.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:231
  - 代码: `result3.get('outputs', {})`
  - 建议: 使用 aiohttp

- **result4.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:236
  - 代码: `result4.get('outputs', {})`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:241
  - 代码: `result5.get('plan', {})`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:242
  - 代码: `result5.get('plan', {})`
  - 建议: 使用 aiohttp

- **result5.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:243
  - 代码: `result5.get('plan', {})`
  - 建议: 使用 aiohttp

- **result6.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:266
  - 代码: `result6.get('success')`
  - 建议: 使用 aiohttp

- **result6.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:268
  - 代码: `result6.get('filepath')`
  - 建议: 使用 aiohttp

- **result6.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:270
  - 代码: `result6.get('error')`
  - 建议: 使用 aiohttp

- **result7.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:280
  - 代码: `result7.get('success')`
  - 建议: 使用 aiohttp

- **result7.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:281
  - 代码: `result7.get('plans', [])`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:284
  - 代码: `plan.get('filename')`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:284
  - 代码: `plan.get('size')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:324
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:332
  - 代码: `result.get('count', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:357
  - 代码: `result.get('models', [])`
  - 建议: 使用 aiohttp

- **model.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:360
  - 代码: `model.get('name')`
  - 建议: 使用 aiohttp

- **model.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:360
  - 代码: `model.get('description')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:371
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:372
  - 代码: `result.get('outputs', {})`
  - 建议: 使用 aiohttp

- **outputs.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:374
  - 代码: `outputs.get('peak_discharge', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:376
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:401
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:403
  - 代码: `result.get('filepath')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:411
  - 代码: `result2.get('success')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:413
  - 代码: `result2.get('output_file')`
  - 建议: 使用 aiohttp

- **result2.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:415
  - 代码: `result2.get('error')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:417
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **r.get**
  - 位置: tests\mcp\test_mcp_full_agent.py:449
  - 代码: `r.get('success')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_full_agent.py:468
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **subprocess.Popen**
  - 位置: tests\mcp\test_mcp_pipeline.py:42
  - 代码: `subprocess.Popen([sys.executable, '-m', module_path], cwd=str(self.project_root), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)`
  - 建议: 使用 aiofiles 替代

- **time.sleep**
  - 位置: tests\mcp\test_mcp_pipeline.py:51
  - 代码: `time.sleep(1)`
  - 建议: 使用 asyncio.sleep

- **pipeline.run**
  - 位置: tests\mcp\test_mcp_pipeline.py:161
  - 代码: `pipeline.run(user_input)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **node.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:173
  - 代码: `node.get('node_id')`
  - 建议: 使用 aiohttp

- **node.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:173
  - 代码: `node.get('task_type')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: tests\mcp\test_mcp_pipeline.py:232
  - 代码: `pipeline.run(user_input)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **node.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:244
  - 代码: `node.get('node_id', 'unknown')`
  - 建议: 使用 aiohttp

- **node.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:245
  - 代码: `node.get('task_type', 'unknown')`
  - 建议: 使用 aiohttp

- **res.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:252
  - 代码: `res.get('node_id', 'unknown')`
  - 建议: 使用 aiohttp

- **res.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:253
  - 代码: `res.get('status', 'unknown')`
  - 建议: 使用 aiohttp

- **call.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:268
  - 代码: `call.get('tool', 'unknown')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:303
  - 代码: `tool.get('name', 'unknown')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:304
  - 代码: `tool.get('description', '')`
  - 建议: 使用 aiohttp

- **t.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:309
  - 代码: `t.get('name', '')`
  - 建议: 使用 aiohttp

- **tool.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:313
  - 代码: `tool.get('name')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\mcp\test_mcp_pipeline.py:341
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **time.sleep**
  - 位置: tests\mcp\test_mcp_pipeline.py:355
  - 代码: `time.sleep(3)`
  - 建议: 使用 asyncio.sleep

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_pipeline.py:367
  - 代码: `asyncio.run(test_mcp_tools_directly())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **result.get**
  - 位置: tests\mcp\test_mcp_simple.py:60
  - 代码: `result.get('success')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_simple.py:62
  - 代码: `result.get('filepath')`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: tests\mcp\test_mcp_simple.py:64
  - 代码: `result.get('error')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_mcp_simple.py:134
  - 代码: `asyncio.run(main())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **manager.clients.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:33
  - 代码: `manager.clients.get('rainfall')`
  - 建议: 使用 aiohttp

- **status_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:45
  - 代码: `status_result.get('success')`
  - 建议: 使用 aiohttp

- **status_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:49
  - 代码: `status_result.get('providers', {})`
  - 建议: 使用 aiohttp

- **p.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:50
  - 代码: `p.get('has_api_key')`
  - 建议: 使用 aiohttp

- **current_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:70
  - 代码: `current_result.get('success')`
  - 建议: 使用 aiohttp

- **current_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:71
  - 代码: `current_result.get('success')`
  - 建议: 使用 aiohttp

- **current_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:72
  - 代码: `current_result.get('current', {})`
  - 建议: 使用 aiohttp

- **current_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:73
  - 代码: `current_result.get('city')`
  - 建议: 使用 aiohttp

- **current.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:74
  - 代码: `current.get('temperature')`
  - 建议: 使用 aiohttp

- **current.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:75
  - 代码: `current.get('weather')`
  - 建议: 使用 aiohttp

- **current.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:76
  - 代码: `current.get('rain_1h', current.get('precipitation', 0))`
  - 建议: 使用 aiohttp

- **current.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:76
  - 代码: `current.get('precipitation', 0)`
  - 建议: 使用 aiohttp

- **forecast_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:88
  - 代码: `forecast_result.get('success')`
  - 建议: 使用 aiohttp

- **forecast_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:89
  - 代码: `forecast_result.get('success')`
  - 建议: 使用 aiohttp

- **forecast_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:90
  - 代码: `forecast_result.get('forecasts', [])`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:93
  - 代码: `f.get('date')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:93
  - 代码: `f.get('datetime', '')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:94
  - 代码: `f.get('precipitation')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:94
  - 代码: `f.get('rain_3h', 0)`
  - 建议: 使用 aiohttp

- **hourly_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:107
  - 代码: `hourly_result.get('success')`
  - 建议: 使用 aiohttp

- **hourly_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:108
  - 代码: `hourly_result.get('success')`
  - 建议: 使用 aiohttp

- **hourly_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:109
  - 代码: `hourly_result.get('forecasts', [])`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:112
  - 代码: `f.get('datetime')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:112
  - 代码: `f.get('date', '')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:113
  - 代码: `f.get('precipitation')`
  - 建议: 使用 aiohttp

- **f.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:113
  - 代码: `f.get('rain_3h', 0)`
  - 建议: 使用 aiohttp

- **coords_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:126
  - 代码: `coords_result.get('success')`
  - 建议: 使用 aiohttp

- **coords_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:127
  - 代码: `coords_result.get('success')`
  - 建议: 使用 aiohttp

- **coords_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:128
  - 代码: `coords_result.get('coordinates', {})`
  - 建议: 使用 aiohttp

- **coords_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:129
  - 代码: `coords_result.get('current', {})`
  - 建议: 使用 aiohttp

- **coords.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:130
  - 代码: `coords.get('lat')`
  - 建议: 使用 aiohttp

- **coords.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:130
  - 代码: `coords.get('lon')`
  - 建议: 使用 aiohttp

- **coords_result.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:131
  - 代码: `coords_result.get('location', 'N/A')`
  - 建议: 使用 aiohttp

- **current.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:132
  - 代码: `current.get('temperature')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\mcp\test_rainfall_mcp.py:157
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_rainfall_mcp.py:162
  - 代码: `asyncio.run(test_rainfall_mcp())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\mcp\test_web_search_server.py:27
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:50
  - 代码: `data.get('api_key_configured')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:51
  - 代码: `data.get('api_status')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:53
  - 代码: `data.get('available_models')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:56
  - 代码: `data.get('error')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:59
  - 代码: `data.get('api_status')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:77
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:79
  - 代码: `data.get('answer', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:80
  - 代码: `data.get('citations', [])`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:82
  - 代码: `data.get('results')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:88
  - 代码: `data.get('error')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:90
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:108
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:110
  - 代码: `data.get('answer', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:112
  - 代码: `data.get('error')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:114
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:132
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:134
  - 代码: `data.get('answer', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:136
  - 代码: `data.get('error')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:138
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:156
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:158
  - 代码: `data.get('content', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:162
  - 代码: `data.get('error')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: tests\mcp\test_web_search_server.py:164
  - 代码: `data.get('success')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_web_search_server.py:209
  - 代码: `asyncio.run(run_all_tests())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **manager.clients.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:33
  - 代码: `manager.clients.get('yolo_vision')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:45
  - 代码: `info_result.get('success')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:46
  - 代码: `info_result.get('error', '')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:49
  - 代码: `info_result.get('install_command')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:56
  - 代码: `info_result.get('pytorch_version')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:57
  - 代码: `info_result.get('ultralytics_version')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:58
  - 代码: `info_result.get('device')`
  - 建议: 使用 aiohttp

- **info_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:59
  - 代码: `info_result.get('cuda_available')`
  - 建议: 使用 aiohttp

- **dataset_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:66
  - 代码: `dataset_result.get('success')`
  - 建议: 使用 aiohttp

- **dataset_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:68
  - 代码: `dataset_result.get('success')`
  - 建议: 使用 aiohttp

- **dataset_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:72
  - 代码: `dataset_result.get('dataset_dir')`
  - 建议: 使用 aiohttp

- **dataset_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:73
  - 代码: `dataset_result.get('created_files', [])`
  - 建议: 使用 aiohttp

- **flood_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:86
  - 代码: `flood_result.get('success')`
  - 建议: 使用 aiohttp

- **flood_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:87
  - 代码: `flood_result.get('detection_count', 0)`
  - 建议: 使用 aiohttp

- **flood_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:88
  - 代码: `flood_result.get('device')`
  - 建议: 使用 aiohttp

- **water_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:99
  - 代码: `water_result.get('success')`
  - 建议: 使用 aiohttp

- **water_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:100
  - 代码: `water_result.get('detection_count', 0)`
  - 建议: 使用 aiohttp

- **infra_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:111
  - 代码: `infra_result.get('success')`
  - 建议: 使用 aiohttp

- **infra_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:112
  - 代码: `infra_result.get('detection_count', 0)`
  - 建议: 使用 aiohttp

- **batch_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:121
  - 代码: `batch_result.get('success')`
  - 建议: 使用 aiohttp

- **batch_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:122
  - 代码: `batch_result.get('total_images', 0)`
  - 建议: 使用 aiohttp

- **batch_result.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:123
  - 代码: `batch_result.get('processed', 0)`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:146
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **asyncio.run**
  - 位置: tests\mcp\test_yolo_vision_mcp.py:151
  - 代码: `asyncio.run(test_yolo_vision_mcp())`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: tests\plan\test_mode_integration.py:189
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:389
  - 代码: `open(plan_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:390
  - 代码: `f.write(plan_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:439
  - 代码: `open(spec_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:440
  - 代码: `f.write(spec_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:470
  - 代码: `open(tasks_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:471
  - 代码: `f.write(tasks_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:487
  - 代码: `open(checklist_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:488
  - 代码: `f.write(checklist_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:499
  - 代码: `open(plan_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: tests\plan\test_plan_spec_integration.py:500
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:530
  - 代码: `open(doc_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:531
  - 代码: `f.write(initial_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:534
  - 代码: `open(doc_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: tests\plan\test_plan_spec_integration.py:535
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:544
  - 代码: `open(doc_path, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_integration.py:545
  - 代码: `f.write(updated_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_integration.py:548
  - 代码: `open(doc_path, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: tests\plan\test_plan_spec_integration.py:549
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:227
  - 代码: `open(filepath, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:228
  - 代码: `f.write(f'# {filename}\n')`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:411
  - 代码: `open(test_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:412
  - 代码: `f.write(test_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:414
  - 代码: `open(test_file, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: tests\plan\test_plan_spec_mode.py:415
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:425
  - 代码: `open(test_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:426
  - 代码: `f.write(test_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:430
  - 代码: `open(test_file, 'r', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.read**
  - 位置: tests\plan\test_plan_spec_mode.py:431
  - 代码: `f.read()`
  - 建议: 使用异步读取方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:444
  - 代码: `open(test_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:445
  - 代码: `f.write(original_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:455
  - 代码: `open(test_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:456
  - 代码: `f.write(new_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:538
  - 代码: `open(plan_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:539
  - 代码: `f.write(plan_content)`
  - 建议: 使用异步写入方法

- **open**
  - 位置: tests\plan\test_plan_spec_mode.py:571
  - 代码: `open(spec_file, 'w', encoding='utf-8')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\plan\test_plan_spec_mode.py:572
  - 代码: `f.write(spec_content)`
  - 建议: 使用异步写入方法

- **urllib.request.Request**
  - 位置: tests\scripts\download_flood_dataset.py:39
  - 代码: `urllib.request.Request(url, headers=headers)`
  - 建议: 使用 aiohttp

- **urllib.request.urlopen**
  - 位置: tests\scripts\download_flood_dataset.py:40
  - 代码: `urllib.request.urlopen(req, timeout=30)`
  - 建议: 使用 aiofiles 替代

- **open**
  - 位置: tests\scripts\download_flood_dataset.py:41
  - 代码: `open(save_path, 'wb')`
  - 建议: 使用 aiofiles 替代

- **f.write**
  - 位置: tests\scripts\download_flood_dataset.py:42
  - 代码: `f.write(response.read())`
  - 建议: 使用异步写入方法

- **response.read**
  - 位置: tests\scripts\download_flood_dataset.py:42
  - 代码: `response.read()`
  - 建议: 使用异步读取方法

- **capsys.readouterr**
  - 位置: tests\unit\test_kimi_guard.py:13
  - 代码: `capsys.readouterr()`
  - 建议: 使用异步读取方法

- **client.post**
  - 位置: tests\unit\test_plans_api.py:69
  - 代码: `client.post('/api/plans/plan_001/generate', json={'user_input': '设计洪水预警系统'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_plans_api.py:89
  - 代码: `client.post('/api/plans/plan_001/modify', json={'instruction': '添加更多细节'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_plans_api.py:104
  - 代码: `client.post('/api/plans/nonexistent/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_plans_api.py:120
  - 代码: `client.post('/api/plans/plan_001/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_plans_api.py:140
  - 代码: `client.post('/api/plans/plan_001/cancel', json={'reason': '用户取消'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_specs_api.py:68
  - 代码: `client.post('/api/specs/feature_001/generate', json={'user_input': '实现洪水预警模块'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_specs_api.py:88
  - 代码: `client.post('/api/specs/feature_001/modify', json={'instruction': '优化性能要求'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_specs_api.py:103
  - 代码: `client.post('/api/specs/nonexistent/modify', json={'instruction': '修改'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_specs_api.py:119
  - 代码: `client.post('/api/specs/feature_001/confirm', json={'action': 'proceed'})`
  - 建议: 使用 aiohttp

- **client.post**
  - 位置: tests\unit\test_specs_api.py:139
  - 代码: `client.post('/api/specs/feature_001/cancel', json={'reason': '需求变更'})`
  - 建议: 使用 aiohttp

- **mock_openai.assert_called_once**
  - 位置: tests\unit\test_websocket_handlers.py:33
  - 代码: `mock_openai.assert_called_once()`
  - 建议: 使用 aiofiles 替代

- **kwargs.get**
  - 位置: tests\unit\agents\task_executor\test_streaming_executor.py:106
  - 代码: `kwargs.get('node_id', args[0] if args else '')`
  - 建议: 使用 aiohttp

- **os.environ.get**
  - 位置: web\debug_pipeline.py:15
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: web\debug_pipeline.py:111
  - 代码: `pipeline.run({'type': 'natural_language', 'input': message})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: web\debug_pipeline2.py:27
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: web\debug_pipeline2.py:58
  - 代码: `pipeline.run({'type': 'natural_language', 'input': message})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: web\debug_pipeline3.py:13
  - 代码: `os.environ.get('KIMI_API_KEY')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: web\debug_pipeline3.py:44
  - 代码: `pipeline.run({'type': 'natural_language', 'input': message})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **requests.get**
  - 位置: web\test_end_to_end.py:23
  - 代码: `requests.get(f'{BASE_URL}/api/health')`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: web\test_end_to_end.py:36
  - 代码: `requests.post(f'{BASE_URL}/api/conversations', json={'title': '测试对话'})`
  - 建议: 使用 aiohttp

- **requests.post**
  - 位置: web\test_end_to_end.py:58
  - 代码: `requests.post(f'{BASE_URL}/api/chat', json={'message': message, 'conversation_id': conversation_id, 'stream': True}, stream=True)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\test_end_to_end.py:81
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\test_end_to_end.py:93
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\test_end_to_end.py:96
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **requests.get**
  - 位置: web\test_end_to_end.py:122
  - 代码: `requests.get(f'{BASE_URL}/api/conversations/{conversation_id}/messages')`
  - 建议: 使用 aiohttp

- **requests.get**
  - 位置: web\test_end_to_end.py:142
  - 代码: `requests.get(f'{BASE_URL}/api/conversations/{conversation_id}/process-events')`
  - 建议: 使用 aiohttp

- **app.get**
  - 位置: web\backend\main.py:69
  - 代码: `app.get('/api/health')`
  - 建议: 使用 aiohttp

- **uvicorn.run**
  - 位置: web\backend\main.py:104
  - 代码: `uvicorn.run(app, host='0.0.0.0', port=port)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **router.post**
  - 位置: web\backend\api\chain_generation.py:98
  - 代码: `router.post('/generate', response_model=ChainGenerationResponse)`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\chain_generation.py:163
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\chain_generation.py:164
  - 代码: `metadata.get('status')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\chain_generation.py:174
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chain_generation.py:143
  - 代码: `router.post('/generate-from-plan', response_model=ChainGenerationResponse)`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\chain_generation.py:220
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\chain_generation.py:221
  - 代码: `metadata.get('status')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\chain_generation.py:231
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chain_generation.py:200
  - 代码: `router.post('/generate-from-spec', response_model=ChainGenerationResponse)`
  - 建议: 使用 aiohttp

- **gen_info.get**
  - 位置: web\backend\api\chain_generation.py:273
  - 代码: `gen_info.get('status', 'unknown')`
  - 建议: 使用 aiohttp

- **gen_info.get**
  - 位置: web\backend\api\chain_generation.py:274
  - 代码: `gen_info.get('progress', 0.0)`
  - 建议: 使用 aiohttp

- **gen_info.get**
  - 位置: web\backend\api\chain_generation.py:275
  - 代码: `gen_info.get('tasks')`
  - 建议: 使用 aiohttp

- **gen_info.get**
  - 位置: web\backend\api\chain_generation.py:276
  - 代码: `gen_info.get('result')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\chain_generation.py:257
  - 代码: `router.get('/{generation_id}/status', response_model=ChainStatusResponse)`
  - 建议: 使用 aiohttp

- **gen_info.get**
  - 位置: web\backend\api\chain_generation.py:299
  - 代码: `gen_info.get('status')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chain_generation.py:284
  - 代码: `router.post('/{generation_id}/execute', response_model=ChainExecutionResponse)`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:347
  - 代码: `exec_info.get('generation_id', '')`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:348
  - 代码: `exec_info.get('status', 'unknown')`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:349
  - 代码: `exec_info.get('progress', 0.0)`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:350
  - 代码: `exec_info.get('tasks')`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:351
  - 代码: `exec_info.get('result')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\chain_generation.py:332
  - 代码: `router.get('/executions/{execution_id}/status', response_model=ChainStatusResponse)`
  - 建议: 使用 aiohttp

- **exec_info.get**
  - 位置: web\backend\api\chain_generation.py:372
  - 代码: `exec_info.get('status')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chain_generation.py:359
  - 代码: `router.post('/executions/{execution_id}/cancel')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: web\backend\api\chat.py:118
  - 代码: `context.get('user_input', '')`
  - 建议: 使用 aiohttp

- **context.get**
  - 位置: web\backend\api\chat.py:119
  - 代码: `context.get('task_type', '')`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: web\backend\api\chat.py:182
  - 代码: `self._task_info_map.get(node_id, {})`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: web\backend\api\chat.py:197
  - 代码: `self._task_info_map.get(node_id, {})`
  - 建议: 使用 aiohttp

- **self._task_info_map.get**
  - 位置: web\backend\api\chat.py:214
  - 代码: `self._task_info_map.get(node_id, {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: web\backend\api\chat.py:260
  - 代码: `result.get('data_pool_snapshot', {})`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: web\backend\api\chat.py:261
  - 代码: `result.get('execution_summary', {})`
  - 建议: 使用 aiohttp

- **task_list_event.data.get**
  - 位置: web\backend\api\chat.py:279
  - 代码: `task_list_event.data.get('tasks', [])`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: web\backend\api\chat.py:281
  - 代码: `task.get('task_id', '')`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: web\backend\api\chat.py:282
  - 代码: `task.get('task_name', '')`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: web\backend\api\chat.py:283
  - 代码: `task.get('task_type', '')`
  - 建议: 使用 aiohttp

- **task.get**
  - 位置: web\backend\api\chat.py:284
  - 代码: `task.get('dependencies', [])`
  - 建议: 使用 aiohttp

- **call.data.get**
  - 位置: web\backend\api\chat.py:298
  - 代码: `call.data.get('caller_agent', '')`
  - 建议: 使用 aiohttp

- **call.data.get**
  - 位置: web\backend\api\chat.py:299
  - 代码: `call.data.get('callee_agent', '')`
  - 建议: 使用 aiohttp

- **call.data.get**
  - 位置: web\backend\api\chat.py:300
  - 代码: `call.data.get('input_summary', '')`
  - 建议: 使用 aiohttp

- **event.data.get**
  - 位置: web\backend\api\chat.py:313
  - 代码: `event.data.get('node_id', '')`
  - 建议: 使用 aiohttp

- **event.data.get**
  - 位置: web\backend\api\chat.py:318
  - 代码: `event.data.get('task_name', node_id)`
  - 建议: 使用 aiohttp

- **event.data.get**
  - 位置: web\backend\api\chat.py:321
  - 代码: `event.data.get('duration_ms', 0)`
  - 建议: 使用 aiohttp

- **event.data.get**
  - 位置: web\backend\api\chat.py:326
  - 代码: `event.data.get('output_summary', '')`
  - 建议: 使用 aiohttp

- **event.data.get**
  - 位置: web\backend\api\chat.py:329
  - 代码: `event.data.get('error_message', '未知错误')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: web\backend\api\chat.py:341
  - 代码: `snapshot.get('tool_name', '')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: web\backend\api\chat.py:342
  - 代码: `snapshot.get('data', {})`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: web\backend\api\chat.py:343
  - 代码: `snapshot.get('success', False)`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:346
  - 代码: `tool_data.get('checks', [])`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:347
  - 代码: `tool_data.get('all_passed', False)`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:348
  - 代码: `tool_data.get('overall_score', 0)`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:349
  - 代码: `tool_data.get('status', '')`
  - 建议: 使用 aiohttp

- **check.get**
  - 位置: web\backend\api\chat.py:360
  - 代码: `check.get('item', '')`
  - 建议: 使用 aiohttp

- **check.get**
  - 位置: web\backend\api\chat.py:361
  - 代码: `check.get('passed', False)`
  - 建议: 使用 aiohttp

- **check.get**
  - 位置: web\backend\api\chat.py:362
  - 代码: `check.get('score', 0)`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:369
  - 代码: `tool_data.get('dispatch_order_text', '')`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:378
  - 代码: `tool_data.get('report', {})`
  - 建议: 使用 aiohttp

- **report.get**
  - 位置: web\backend\api\chat.py:379
  - 代码: `report.get('report_content', '')`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:386
  - 代码: `tool_data.get('answer', '')`
  - 建议: 使用 aiohttp

- **tool_data.get**
  - 位置: web\backend\api\chat.py:387
  - 代码: `tool_data.get('question', '')`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: web\backend\api\chat.py:412
  - 代码: `snapshot.get('answer', '')`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: web\backend\api\chat.py:419
  - 代码: `execution_summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: web\backend\api\chat.py:420
  - 代码: `execution_summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: web\backend\api\chat.py:421
  - 代码: `execution_summary.get('failed_tasks', 0)`
  - 建议: 使用 aiohttp

- **execution_summary.get**
  - 位置: web\backend\api\chat.py:422
  - 代码: `execution_summary.get('total_duration_ms', 0)`
  - 建议: 使用 aiohttp

- **result.get**
  - 位置: web\backend\api\chat.py:437
  - 代码: `result.get('success', False)`
  - 建议: 使用 aiohttp

- **snapshot.get**
  - 位置: web\backend\api\chat.py:443
  - 代码: `snapshot.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **pipeline.run**
  - 位置: web\backend\api\chat.py:562
  - 代码: `pipeline.run({'type': 'natural_language', 'input': message})`
  - 建议: 使用 asyncio.create_subprocess_exec

- **asyncio.sleep**
  - 位置: web\backend\api\chat.py:581
  - 代码: `asyncio.sleep(0.01)`
  - 建议: 使用 asyncio.sleep

- **asyncio.sleep**
  - 位置: web\backend\api\chat.py:603
  - 代码: `asyncio.sleep(0.02)`
  - 建议: 使用 asyncio.sleep

- **data.get**
  - 位置: web\backend\api\chat.py:649
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\api\chat.py:650
  - 代码: `data.get('content', '')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\api\chat.py:651
  - 代码: `data.get('conversation_id')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\api\chat.py:652
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\api\chat.py:653
  - 代码: `data.get('content')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chat.py:628
  - 代码: `router.post('/chat')`
  - 建议: 使用 aiohttp

- **_messages.get**
  - 位置: web\backend\api\chat.py:664
  - 代码: `_messages.get(conversation_id, [])`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\chat.py:661
  - 代码: `router.get('/conversations/{conversation_id}/messages')`
  - 建议: 使用 aiohttp

- **_process_events.get**
  - 位置: web\backend\api\chat.py:678
  - 代码: `_process_events.get(conversation_id, [])`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\chat.py:675
  - 代码: `router.get('/conversations/{conversation_id}/process-events')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\chat.py:689
  - 代码: `router.post('/conversations/{conversation_id}/clear')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\conversations.py:55
  - 代码: `router.get('/conversations', response_model=List[ConversationResponse])`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\conversations.py:79
  - 代码: `router.post('/conversations', response_model=ConversationResponse)`
  - 建议: 使用 aiohttp

- **_conversations.get**
  - 位置: web\backend\api\conversations.py:124
  - 代码: `_conversations.get(conversation_id)`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\conversations.py:111
  - 代码: `router.get('/conversations/{conversation_id}', response_model=ConversationResponse)`
  - 建议: 使用 aiohttp

- **plan.get**
  - 位置: web\backend\api\conversations.py:261
  - 代码: `plan.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:264
  - 代码: `metadata.get('title', '未命名规划')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:265
  - 代码: `metadata.get('status', 'draft')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:266
  - 代码: `metadata.get('version', 1)`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:267
  - 代码: `metadata.get('created_at')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:268
  - 代码: `metadata.get('updated_at')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\conversations.py:227
  - 代码: `router.get('/conversations/{conversation_id}/plans', response_model=PlanListResponse)`
  - 建议: 使用 aiohttp

- **spec.get**
  - 位置: web\backend\api\conversations.py:326
  - 代码: `spec.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:329
  - 代码: `metadata.get('feature_name', spec['document_id'])`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:330
  - 代码: `metadata.get('display_name', '未命名规格')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:331
  - 代码: `metadata.get('status', 'draft')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:332
  - 代码: `metadata.get('version', 1)`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:333
  - 代码: `metadata.get('created_at')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\conversations.py:334
  - 代码: `metadata.get('updated_at')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\conversations.py:292
  - 代码: `router.get('/conversations/{conversation_id}/specs', response_model=SpecListResponse)`
  - 建议: 使用 aiohttp

- **schema_map.get**
  - 位置: web\backend\api\data_acquisition.py:181
  - 代码: `schema_map.get(request.schema_type)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:162
  - 代码: `router.post('/parse', response_model=ParseInputResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:201
  - 代码: `router.post('/confirm', response_model=ConfirmDataResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:230
  - 代码: `router.post('/request', response_model=DataRequestResponse)`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\data_acquisition.py:274
  - 代码: `router.get('/defaults', response_model=DefaultValuesResponse)`
  - 建议: 使用 aiohttp

- **lineage.get**
  - 位置: web\backend\api\data_acquisition.py:321
  - 代码: `lineage.get('path', [])`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\data_acquisition.py:306
  - 代码: `router.get('/lineage/{data_key}', response_model=LineageResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:335
  - 代码: `router.post('/clarification/session', response_model=ClarificationSessionResponse)`
  - 建议: 使用 aiohttp

- **clarification_manager.skip_request**
  - 位置: web\backend\api\data_acquisition.py:392
  - 代码: `clarification_manager.skip_request(session_id=request.session_id, request_id=request.request_id)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:366
  - 代码: `router.post('/clarification/resolve', response_model=ClarificationResolveResponse)`
  - 建议: 使用 aiohttp

- **file.read**
  - 位置: web\backend\api\data_acquisition.py:422
  - 代码: `file.read()`
  - 建议: 使用异步读取方法

- **pd.read_csv**
  - 位置: web\backend\api\data_acquisition.py:428
  - 代码: `pd.read_csv(io.StringIO(content.decode('utf-8')))`
  - 建议: 使用异步读取方法

- **pd.read_excel**
  - 位置: web\backend\api\data_acquisition.py:433
  - 代码: `pd.read_excel(io.BytesIO(content))`
  - 建议: 使用异步读取方法

- **router.post**
  - 位置: web\backend\api\data_acquisition.py:411
  - 代码: `router.post('/upload')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\mode.py:124
  - 代码: `router.post('/mode/detect', response_model=ModeDetectResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:91
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:142
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:147
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\plans.py:114
  - 代码: `router.post('/{plan_id}/generate', response_model=PlanResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:187
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:194
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\plans.py:166
  - 代码: `router.post('/{plan_id}/modify', response_model=PlanResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:232
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:238
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\plans.py:214
  - 代码: `router.post('/{plan_id}/confirm', response_model=PlanResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:276
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\plans.py:282
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\plans.py:259
  - 代码: `router.post('/{plan_id}/cancel', response_model=PlanResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\sessions.py:156
  - 代码: `router.post('', response_model=CreateSessionResponse)`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\sessions.py:180
  - 代码: `router.get('/{session_id}/status', response_model=SessionStatusResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\sessions.py:205
  - 代码: `router.post('/{session_id}/resume', response_model=ResumeSessionResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\sessions.py:237
  - 代码: `router.post('/{session_id}/update', response_model=SessionStatusResponse)`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\sessions.py:291
  - 代码: `router.get('', response_model=List[SessionStatusResponse])`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\sessions.py:327
  - 代码: `router.post('/resume', response_model=ResumeSessionResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:86
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:137
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:142
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:109
  - 代码: `router.post('/{feature_name}/generate', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:182
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:189
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:161
  - 代码: `router.post('/{feature_name}/modify', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:227
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:233
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:209
  - 代码: `router.post('/{feature_name}/confirm', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:271
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:277
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:254
  - 代码: `router.post('/{feature_name}/cancel', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:324
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\specs.py:327
  - 代码: `metadata.get('display_name', doc['document_id'])`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\specs.py:328
  - 代码: `metadata.get('status', 'draft')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:329
  - 代码: `doc.get('created_at')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:330
  - 代码: `doc.get('updated_at')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\specs.py:312
  - 代码: `router.get('', response_model=list)`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:351
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:354
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\specs.py:360
  - 代码: `metadata.get('display_name', feature_name)`
  - 建议: 使用 aiohttp

- **metadata.get**
  - 位置: web\backend\api\specs.py:361
  - 代码: `metadata.get('status', 'draft')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:365
  - 代码: `doc.get('created_at')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:366
  - 代码: `doc.get('updated_at')`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\specs.py:338
  - 代码: `router.get('/{feature_name}', response_model=Dict[str, Any])`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:388
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **info.get**
  - 位置: web\backend\api\specs.py:397
  - 代码: `info.get('title', name)`
  - 建议: 使用 aiohttp

- **info.get**
  - 位置: web\backend\api\specs.py:398
  - 代码: `info.get('sections', [])`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\specs.py:374
  - 代码: `router.get('/{feature_name}/files', response_model=SpecFilesListResponse)`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:423
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\api\specs.py:424
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **file_mapping.get**
  - 位置: web\backend\api\specs.py:439
  - 代码: `file_mapping.get(file_name, file_name)`
  - 建议: 使用 aiohttp

- **file_info.get**
  - 位置: web\backend\api\specs.py:450
  - 代码: `file_info.get('content', '')`
  - 建议: 使用 aiohttp

- **file_info.get**
  - 位置: web\backend\api\specs.py:452
  - 代码: `file_info.get('title', '')`
  - 建议: 使用 aiohttp

- **file_info.get**
  - 位置: web\backend\api\specs.py:453
  - 代码: `file_info.get('sections', [])`
  - 建议: 使用 aiohttp

- **router.get**
  - 位置: web\backend\api\specs.py:409
  - 代码: `router.get('/{feature_name}/{file_name}', response_model=SpecFileResponse)`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:462
  - 代码: `router.post('', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:507
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:549
  - 代码: `existing.get('content', '')`
  - 建议: 使用 aiohttp

- **existing.get**
  - 位置: web\backend\api\specs.py:553
  - 代码: `existing.get('metadata', {})`
  - 建议: 使用 aiohttp

- **router.post**
  - 位置: web\backend\api\specs.py:574
  - 代码: `router.post('/{feature_name}/approve', response_model=SpecResponse)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\chat_ws.py:137
  - 代码: `message.get('type', 'unknown')`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\websocket\message_handlers.py:56
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:97
  - 代码: `message.get('content', '')`
  - 建议: 使用 aiohttp

- **generation_metadata.get**
  - 位置: web\backend\websocket\message_handlers.py:216
  - 代码: `generation_metadata.get('optimization', {})`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:343
  - 代码: `summary.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:345
  - 代码: `summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:346
  - 代码: `summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:347
  - 代码: `summary.get('failed_tasks', 0)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:388
  - 代码: `message.get('plan_id', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:389
  - 代码: `message.get('action', 'confirm')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\websocket\message_handlers.py:439
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\websocket\message_handlers.py:440
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **generation_metadata.get**
  - 位置: web\backend\websocket\message_handlers.py:511
  - 代码: `generation_metadata.get('reliability_score', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:634
  - 代码: `summary.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:636
  - 代码: `summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:637
  - 代码: `summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:672
  - 代码: `message.get('feature_name', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:673
  - 代码: `message.get('action', 'confirm')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\websocket\message_handlers.py:723
  - 代码: `doc.get('content', '')`
  - 建议: 使用 aiohttp

- **doc.get**
  - 位置: web\backend\websocket\message_handlers.py:724
  - 代码: `doc.get('metadata', {})`
  - 建议: 使用 aiohttp

- **generation_metadata.get**
  - 位置: web\backend\websocket\message_handlers.py:795
  - 代码: `generation_metadata.get('reliability_score', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:918
  - 代码: `summary.get('error', '未知错误')`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:920
  - 代码: `summary.get('total_tasks', 0)`
  - 建议: 使用 aiohttp

- **summary.get**
  - 位置: web\backend\websocket\message_handlers.py:921
  - 代码: `summary.get('completed_tasks', 0)`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:937
  - 代码: `message.get('operation_type', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:938
  - 代码: `message.get('operation_id', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:939
  - 代码: `message.get('reason', '用户请求')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:970
  - 代码: `message.get('user_input', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:971
  - 代码: `message.get('plan_id')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: web\backend\websocket\message_handlers.py:1042
  - 代码: `asyncio.sleep(0.01)`
  - 建议: 使用 asyncio.sleep

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:1098
  - 代码: `message.get('user_input', '')`
  - 建议: 使用 aiohttp

- **message.get**
  - 位置: web\backend\websocket\message_handlers.py:1099
  - 代码: `message.get('feature_name')`
  - 建议: 使用 aiohttp

- **asyncio.sleep**
  - 位置: web\backend\websocket\message_handlers.py:1189
  - 代码: `asyncio.sleep(0.01)`
  - 建议: 使用 asyncio.sleep

- **HANDLER_MAP.get**
  - 位置: web\backend\websocket\message_handlers.py:1262
  - 代码: `HANDLER_MAP.get(message_type)`
  - 建议: 使用 aiohttp

- **data.get**
  - 位置: web\backend\websocket\message_types.py:257
  - 代码: `data.get('type')`
  - 建议: 使用 aiohttp

- **MESSAGE_TYPE_MAP.get**
  - 位置: web\backend\websocket\message_types.py:285
  - 代码: `MESSAGE_TYPE_MAP.get(msg_type)`
  - 建议: 使用 aiohttp

- **subprocess.run**
  - 位置: web\deploy\check_env.py:29
  - 代码: `subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)`
  - 建议: 使用 asyncio.create_subprocess_exec

- **os.environ.get**
  - 位置: web\deploy\check_env.py:54
  - 代码: `os.environ.get('CONDA_DEFAULT_ENV', '')`
  - 建议: 使用 aiohttp

### MEDIUM 级别
- **asyncio.Lock**
  - 位置: src\flood_decision_agent\mcp\core\client.py:72
  - 代码: `asyncio.Lock()`
  - 建议: 使用 asyncio.Lock

- **asyncio.Semaphore**
  - 位置: src\flood_decision_agent\mcp\core\server.py:76
  - 代码: `asyncio.Semaphore(config.max_concurrent)`
  - 建议: 使用 asyncio.Semaphore

- **asyncio.Lock**
  - 位置: src\flood_decision_agent\mcp\core\session.py:127
  - 代码: `asyncio.Lock()`
  - 建议: 使用 asyncio.Lock

- **asyncio.Lock**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:69
  - 代码: `asyncio.Lock()`
  - 建议: 使用 asyncio.Lock

### LOW 级别
- **json.loads**
  - 位置: debug\run_debug.py:23
  - 代码: `json.loads(config_path.read_text(encoding='utf-8'))`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: debug\run_debug.py:33
  - 代码: `json.dumps(result.data_pool_snapshot, ensure_ascii=False, default=str, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:91
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\e2e_diagnosis.py:123
  - 代码: `json.dumps({'type': 'chat_message', 'content': '分析长江流域洪水风险', 'mode': 'normal'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:141
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:208
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\e2e_diagnosis.py:222
  - 代码: `json.dumps({'type': 'chat_message', 'content': '制定长江流域洪水应急响应计划', 'mode': 'plan'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:239
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\e2e_diagnosis.py:276
  - 代码: `json.dumps({'type': 'confirm_plan', 'confirmed': True})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:290
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\e2e_diagnosis.py:354
  - 代码: `json.dumps({'type': 'chat_message', 'content': '', 'mode': 'normal'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\e2e_diagnosis.py:363
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\performance_tester.py:110
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\performance_tester.py:128
  - 代码: `json.dumps(message)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\performance_tester.py:172
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\performance_tester.py:177
  - 代码: `json.dumps({'type': 'ping', 'content': f'conn_{conn_id}'})`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: diagnosis\performance_tester.py:228
  - 代码: `json.dumps({'type': 'chat_message', 'content': '分析长江流域洪水风险并生成应对方案', 'mode': 'normal'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: diagnosis\performance_tester.py:244
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: examples\quick_start.py:44
  - 代码: `json.dumps(plan, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: examples\quick_start.py:51
  - 代码: `json.dumps(sorted(snapshot.keys()), ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\summarizer.py:225
  - 代码: `json.dumps(data_pool, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\agents\decision_chain\generator.py:780
  - 代码: `json.loads(user_input)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser.py:225
  - 代码: `json.loads(json_match.group())`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\agents\intent_parser\parser_v2.py:362
  - 代码: `json.loads(json_match.group())`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\decision_generator_prompts.py:29
  - 代码: `json.dumps(data_summary, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\decision_generator_prompts.py:31
  - 代码: `json.dumps(constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\decision_generator_prompts.py:98
  - 代码: `json.dumps(scenario, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\decision_generator_prompts.py:150
  - 代码: `json.dumps(task_results, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\intent_parser_prompts.py:32
  - 代码: `json.dumps(templates, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:151
  - 代码: `json.dumps(context.constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:260
  - 代码: `json.dumps(context.constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:428
  - 代码: `json.dumps(context.constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\plan_spec_prompts.py:757
  - 代码: `json.dumps(context.constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\agents\prompts\task_decomposer_prompts.py:30
  - 代码: `json.dumps(intent, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:279
  - 代码: `json.dumps(result, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:403
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:412
  - 代码: `json.loads(match.strip())`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\application\services\data_acquisition\parser\engine.py:421
  - 代码: `json.loads(brace_match.group(0))`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\conversation\context.py:190
  - 代码: `json.loads(json_str)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\core\message.py:38
  - 代码: `json.dumps(data, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\core\message.py:43
  - 代码: `json.loads(json_str)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\evaluation\core\evaluator.py:99
  - 代码: `json.dumps(test_case.structured_input)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\evaluation\reports\base.py:75
  - 代码: `json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\evaluation\reports\formatters\json_formatter.py:48
  - 代码: `json.dumps(data, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\infrastructure\config_loader.py:99
  - 代码: `json.loads(content)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\infrastructure\config_loader.py:167
  - 代码: `json.loads(value)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\mcp\clients\base.py:128
  - 代码: `json.loads(content.text)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:132
  - 代码: `json.dumps(data, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\mcp\core\transport.py:178
  - 代码: `json.loads(data.decode(self.config.encoding))`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\mcp\protocol\messages.py:114
  - 代码: `json.loads(data)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\protocol\messages.py:140
  - 代码: `json.dumps(message.to_dict(), ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:379
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:430
  - 代码: `json.dumps({'success': True, 'file_path': output_path, 'file_name': os.path.basename(output_path), 'title': title, 'created_at': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:458
  - 代码: `json.dumps({'success': True, 'file_path': plan_path, 'file_name': os.path.basename(plan_path), 'content': content, 'sections': list(sections.keys()), 'parsed_sections': sections, 'size': len(content)}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:495
  - 代码: `json.dumps({'success': True, 'file_path': plan_path, 'updated_section': section, 'updated_at': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:569
  - 代码: `json.dumps({'success': True, 'feature_name': feature_name, 'feature_dir': feature_dir, 'created_files': created_files, 'file_count': len(created_files), 'created_at': created_at}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:598
  - 代码: `json.dumps({'success': True, 'file_path': spec_path, 'file_name': os.path.basename(spec_path), 'content': content, 'sections': list(sections.keys()), 'size': len(content)}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:634
  - 代码: `json.dumps({'success': True, 'file_path': spec_path, 'updated_section': section, 'updated_at': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:681
  - 代码: `json.dumps({'success': True, 'count': len(plans), 'plans': plans}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:714
  - 代码: `json.dumps({'success': True, 'count': len(specs), 'specs': specs}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\decision_chain_server.py:736
  - 代码: `json.dumps({'success': True, 'deleted': doc_path, 'deleted_at': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:157
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:170
  - 代码: `json.dumps({'success': False, 'error': 'python-docx 未安装，请运行: pip install python-docx'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:250
  - 代码: `json.dumps({'success': True, 'input_file': input_file, 'output_file': output_file, 'output_path': output_path, 'paragraphs': len(doc.paragraphs), 'tables': len(doc.tables), 'content_preview': markdown_content[:500] + '...' if len(markdown_content) > 500 else markdown_content}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:308
  - 代码: `json.dumps({'success': False, 'error': 'python-docx 未安装'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:339
  - 代码: `json.dumps({'success': True, 'filename': input_file, 'paragraphs': len(doc.paragraphs), 'tables': len(doc.tables), 'content': content[:2000] + '...' if len(content) > 2000 else content}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:376
  - 代码: `json.dumps({'success': True, 'directory': directory, 'extension': extension, 'count': len(files), 'files': files}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:391
  - 代码: `json.dumps({'success': False, 'error': 'python-docx 未安装，请运行: pip install python-docx'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\document_server.py:456
  - 代码: `json.dumps({'success': True, 'filename': filename, 'filepath': filepath, 'title': title, 'message': '示例文档已创建'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:220
  - 代码: `json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:271
  - 代码: `json.dumps({'success': True, 'filepath': filepath, 'filename': filename, 'plan_name': plan_name, 'created_at': default_metadata['created_at']}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:333
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:362
  - 代码: `json.dumps({'success': True, 'count': len(files), 'plans': files}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:388
  - 代码: `json.dumps({'success': True, 'filepath': filepath, 'message': '内容已追加'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:409
  - 代码: `json.dumps({'success': True, 'deleted': plan_id}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:433
  - 代码: `json.dumps({'success': True, 'filepath': filepath, 'size': os.path.getsize(filepath)}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\filesystem_server.py:456
  - 代码: `json.dumps({'success': True, 'data': data}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:408
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:428
  - 代码: `json.dumps({'success': True, 'models': models, 'total': len(models)}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:470
  - 代码: `json.dumps({'success': True, 'model': {'name': model.name, 'description': model.description, 'parameters': params_info}}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:496
  - 代码: `json.dumps({'success': True, 'model': result.pop('model'), 'inputs': {'rainfall_count': len(inputs['rainfall']), 'catchment_area': inputs['catchment_area']}, 'outputs': result, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:524
  - 代码: `json.dumps({'success': True, 'model': result.pop('model'), 'inputs': {'inflow_count': len(inputs['inflow']), 'k': inputs['k'], 'x': inputs['x']}, 'outputs': result, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:554
  - 代码: `json.dumps({'success': True, 'model': result.pop('model'), 'inputs': {'inflow_count': len(inputs['inflow']), 'initial_level': inputs['initial_level'], 'target_level': inputs['target_level']}, 'outputs': result, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:599
  - 代码: `json.dumps({'success': True, 'plan': plan, 'model_used': 'reservoir_dispatch'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\hydrology_server.py:634
  - 代码: `json.dumps({'success': True, 'is_safe': is_safe, 'violations': violations, 'warnings': warnings, 'plan_id': dispatch_plan.get('plan_id', 'unknown'), 'validation_time': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:254
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:275
  - 代码: `json.dumps(cached, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:286
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:301
  - 代码: `json.dumps(cached, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:312
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:327
  - 代码: `json.dumps(cached, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:338
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:353
  - 代码: `json.dumps(cached, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:364
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\rainfall_server.py:394
  - 代码: `json.dumps(status, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:183
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:198
  - 代码: `json.dumps({'success': False, 'error': '未配置 KIMI_API_KEY 环境变量', 'note': '请设置环境变量: KIMI_API_KEY'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:212
  - 代码: `json.dumps(cached, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:291
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:297
  - 代码: `json.dumps({'success': False, 'error': '搜索请求超时', 'query': query}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:318
  - 代码: `json.dumps({'success': False, 'error': f'URL 验证失败: {e}'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:328
  - 代码: `json.dumps(cached, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:334
  - 代码: `json.dumps({'success': False, 'error': '未配置 KIMI_API_KEY 环境变量'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:404
  - 代码: `json.dumps(result, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:410
  - 代码: `json.dumps({'success': False, 'error': '网页抓取超时', 'url': url}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\web_search_server.py:487
  - 代码: `json.dumps(status, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:127
  - 代码: `json.dumps({'success': False, 'error': f'依赖未安装: {_deps_error}', 'install_command': 'pip install ultralytics opencv-python numpy', 'note': '请在系统 Python 环境中运行上述命令安装依赖'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:287
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:345
  - 代码: `json.dumps({'success': True, 'task': 'flood_detection', 'image_path': image_path, 'detection_count': len(detections), 'detections': detections, 'result_image': result_path, 'device': _get_device(), 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:404
  - 代码: `json.dumps({'success': True, 'task': 'water_body_detection', 'image_path': image_path, 'detection_count': len(detections), 'detections': detections, 'result_image': result_path, 'device': _get_device(), 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:463
  - 代码: `json.dumps({'success': True, 'task': 'infrastructure_detection', 'image_path': image_path, 'detection_count': len(detections), 'detections': detections, 'result_image': result_path, 'device': _get_device(), 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:500
  - 代码: `json.dumps({'success': True, 'task': 'batch_detection', 'image_dir': image_dir, 'total_images': 0, 'processed': 0, 'message': '目录中没有图像文件'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:546
  - 代码: `json.dumps({'success': True, 'task': 'batch_detection', 'image_dir': image_dir, 'total_images': len(image_files), 'processed': len(results_summary), 'device': _get_device(), 'results': results_summary, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:565
  - 代码: `json.dumps({'success': False, 'error': f'依赖未安装: {_deps_error}', 'install_command': 'pip install ultralytics opencv-python numpy', 'note': '请在系统 Python 环境中运行上述命令安装依赖'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:596
  - 代码: `json.dumps({'success': True, 'pytorch_version': torch.__version__, 'ultralytics_version': ultralytics.__version__, 'cuda_available': torch.cuda.is_available(), 'device': device, 'model': model_info, 'models_dir': os.path.abspath(MODELS_DIR), 'datasets_dir': os.path.abspath(DATASETS_DIR), 'results_dir': os.path.abspath(RESULTS_DIR)}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:612
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:626
  - 代码: `json.dumps({'success': False, 'error': f'依赖未安装: {_deps_error}', 'install_command': 'pip install opencv-python numpy', 'note': '请在系统 Python 环境中运行上述命令安装依赖'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:670
  - 代码: `json.dumps({'success': True, 'dataset_name': dataset_name, 'dataset_dir': os.path.abspath(dataset_dir), 'created_files': created_files, 'file_count': len(created_files), 'note': '这是模拟数据集，用于测试 YOLO 检测功能。实际使用时请替换为真实水利图像。'}, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\mcp\servers\yolo_vision_server.py:683
  - 代码: `json.dumps({'success': False, 'error': str(e), 'error_type': type(e).__name__, 'note': '请确保已安装 opencv-python 和 numpy'}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\tools\common_tools.py:252
  - 代码: `json.dumps(data, indent=indent, ensure_ascii=False, default=str)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: src\flood_decision_agent\tools\llm_tools.py:287
  - 代码: `json.loads(tool_call.function.arguments)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: src\flood_decision_agent\tools\llm_tools.py:304
  - 代码: `json.dumps({'result': tool_result}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\comprehensive_api_test.py:185
  - 代码: `json.loads(line_str[6:])`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_chain_generation_api.py:166
  - 代码: `json.loads(result)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\test_chain_generation_api.py:170
  - 代码: `json.dumps({'type': 'ping', 'timestamp': time.time()})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_chain_generation_api.py:172
  - 代码: `json.loads(result)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_chain_generation_api.py:190
  - 代码: `json.loads(result)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\test_chain_generation_api.py:194
  - 代码: `json.dumps({'type': 'generate_chain_normal', 'user_input': '查询今天的水位数据', 'generation_id': 'test_gen_normal_001', 'timestamp': time.time()})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_chain_generation_api.py:207
  - 代码: `json.loads(result)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_websocket_live.py:18
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\test_websocket_live.py:22
  - 代码: `json.dumps({'type': 'ping', 'timestamp': 1234567890})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_websocket_live.py:24
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\test_websocket_live.py:28
  - 代码: `json.dumps({'type': 'chat_message', 'content': '你好', 'role': 'user'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\test_websocket_live.py:38
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\agents\test_decision_chain_generator.py:321
  - 代码: `json.dumps({'task_type': 'flood_dispatch', 'target': {'outflow': 19000}})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_detailed_websocket.py:18
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_detailed_websocket.py:23
  - 代码: `json.dumps({'type': 'chat_message', 'content': '查询今日水位'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_detailed_websocket.py:34
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_simple_websocket.py:18
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_simple_websocket.py:23
  - 代码: `json.dumps({'type': 'chat_message', 'content': '查询今日水位'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_simple_websocket.py:33
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:26
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_websocket_e2e.py:43
  - 代码: `json.dumps({'type': 'ping'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:47
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_websocket_e2e.py:66
  - 代码: `json.dumps({'type': 'chat_message', 'content': '查询今日水位'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:78
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_websocket_e2e.py:118
  - 代码: `json.dumps({'type': 'start_plan', 'user_input': '设计一个洪水预警系统'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:127
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_websocket_e2e.py:148
  - 代码: `json.dumps({'type': 'confirm_plan', 'plan_id': plan_id, 'action': 'confirm'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:159
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\e2e\test_websocket_e2e.py:198
  - 代码: `json.dumps({'type': 'chat_message', 'content': '测试消息序列'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\e2e\test_websocket_e2e.py:208
  - 代码: `json.loads(response)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\integration\test_api_comprehensive.py:125
  - 代码: `json.loads(line_str[6:])`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\integration\test_websocket_chain_generation.py:43
  - 代码: `json.dumps({'type': 'ping'})`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\mcp\test_web_search_server.py:48
  - 代码: `json.loads(result[0].text)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\mcp\test_web_search_server.py:75
  - 代码: `json.loads(result[0].text)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\mcp\test_web_search_server.py:106
  - 代码: `json.loads(result[0].text)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\mcp\test_web_search_server.py:130
  - 代码: `json.loads(result[0].text)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: tests\mcp\test_web_search_server.py:154
  - 代码: `json.loads(result[0].text)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: tests\plan\test_plan_spec_integration.py:581
  - 代码: `json.dumps(constraints, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\test_end_to_end.py:42
  - 代码: `json.dumps(data, indent=2, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: web\test_end_to_end.py:79
  - 代码: `json.loads(line_str[6:])`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:402
  - 代码: `json.dumps(value, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:407
  - 代码: `json.dumps(tool_data, ensure_ascii=False, indent=2)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:483
  - 代码: `json.dumps({'type': 'user_message', 'content': message, 'conversation_id': conversation_id}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:580
  - 代码: `json.dumps(event_data, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:602
  - 代码: `json.dumps({'type': 'chunk', 'content': chunk, 'accumulated': accumulated_content}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:618
  - 代码: `json.dumps({'type': 'complete', 'content': response_text, 'conversation_id': conversation_id}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.dumps**
  - 位置: web\backend\api\chat.py:625
  - 代码: `json.dumps({'type': 'error', 'content': error_message}, ensure_ascii=False)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: web\backend\api\chat.py:648
  - 代码: `json.loads(chunk[6:])`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: web\backend\api\data_acquisition.py:286
  - 代码: `json.loads(conditions)`
  - 建议: 大型数据时使用异步处理

- **json.loads**
  - 位置: web\backend\websocket\chat_ws.py:136
  - 代码: `json.loads(data)`
  - 建议: 大型数据时使用异步处理

## 分析错误

- test_yaml_parse.py: Syntax error - expected '(' (<unknown>, line 55)
- scripts\start_web.py: Syntax error - closing parenthesis ']' does not match opening parenthesis '(' on line 44 (<unknown>, line 45)

================================================================================
报告生成完成
================================================================================