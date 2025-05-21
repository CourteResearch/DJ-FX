INFO:     127.0.0.1:49616 - "GET /api/mixes HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 403, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\applications.py", line 112, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
    raise exc
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
    await self.app(scope, receive, _send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\middleware\cors.py", line 93, in __call__
    await self.simple_response(scope, receive, send, request_headers=headers)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\middleware\cors.py", line 144, in simple_response
    await self.app(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\routing.py", line 714, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\routing.py", line 734, in app
    await route.handle(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\routing.py", line 288, in handle
    await self.app(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\starlette\routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\fastapi\routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\fastapi\routing.py", line 212, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Job\DJ-FX\backend\server.py", line 404, in get_mixes
    mixes = await db.mixes.find(filter_dict).to_list(1000)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\motor\core.py", line 1696, in _to_list
    result = get_more_result.result()
  File "C:\Python313\Lib\concurrent\futures\thread.py", line 59, in run
    result = self.fn(*self.args, **self.kwargs)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\cursor.py", line 1208, in _refresh
    self._send_message(q)
    ~~~~~~~~~~~~~~~~~~^^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\cursor.py", line 1102, in _send_message
    response = client._run_operation(
        operation, self._unpack_response, address=self._address
    )
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\_csot.py", line 119, in csot_wrapper
    return func(self, *args, **kwargs)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 1917, in _run_operation        
    return self._retryable_read(
           ~~~~~~~~~~~~~~~~~~~~^
        _cmd,
        ^^^^^
    ...<4 lines>...
        operation=operation.name,
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 2026, in _retryable_read       
    return self._retry_internal(
           ~~~~~~~~~~~~~~~~~~~~^
        func,
        ^^^^^
    ...<7 lines>...
        operation_id=operation_id,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\_csot.py", line 119, in csot_wrapper
    return func(self, *args, **kwargs)
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 1993, in _retry_internal       
    ).run()
      ~~~^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 2730, in run
    return self._read() if self._is_read else self._write()
           ~~~~~~~~~~^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 2875, in _read
    self._server = self._get_server()
                   ~~~~~~~~~~~~~~~~^^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 2823, in _get_server
    return self._client._select_server(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self._server_selector,
        ^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        operation_id=self._operation_id,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\mongo_client.py", line 1812, in _select_server        
    server = topology.select_server(
        server_selector,
    ...<2 lines>...
        operation_id=operation_id,
    )
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\topology.py", line 409, in select_server
    server = self._select_server(
        selector,
    ...<4 lines>...
        operation_id=operation_id,
    )
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\topology.py", line 387, in _select_server
    servers = self.select_servers(
        selector, operation, server_selection_timeout, address, operation_id
    )
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\topology.py", line 294, in select_servers
    server_descriptions = self._select_servers_loop(
        selector, server_timeout, operation, operation_id, address
    )
  File "D:\Job\DJ-FX\backend\venv\Lib\site-packages\pymongo\synchronous\topology.py", line 344, in _select_servers_loop       
    raise ServerSelectionTimeoutError(
        f"{self._error_message(selector)}, Timeout: {timeout}s, Topology Description: {self.description!r}"
    )
pymongo.errors.ServerSelectionTimeoutError: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 30s, Topology Description: <TopologyDescription id: 682de630a69449065c480f8b, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
2025-05-21 17:50:29,569 - root - ERROR - Error creating mix: localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms), Timeout: 30s, Topology Description: <TopologyDescription id: 682de630a69449065c480f8b, topology_type: Unknown, servers: [<ServerDescription ('localhost', 27017) server_type: Unknown, rtt: None, error=AutoReconnect('localhost:27017: [WinError 10061] No connection could be made because the target machine actively refused it (configured timeouts: socketTimeoutMS: 20000.0ms, connectTimeoutMS: 20000.0ms)')>]>
INFO:     127.0.0.1:49671 - "POST /api/mixes HTTP/1.1" 500 Internal Server Error
