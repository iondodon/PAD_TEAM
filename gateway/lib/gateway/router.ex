defmodule Gateway.Router do
    use Plug.Router
    use Plug.ErrorHandler
    alias Service.CircuiBreaker
    alias Gateway.Cache.ECache

    plug(:match)
    plug(
        Plug.Parsers,
        parsers: [:json, :urlencoded, :multipart],
        pass: ["text/*"],
        json_decoder: Jason
    )
    plug(:dispatch)

    defp handle_requests(conn, service) do
        request = %{
            service: service,
            method: String.to_atom(String.downcase(conn.method, :default)),
            path: conn.request_path,
            body: conn.body_params,
            headers: conn.req_headers
        }

        case CircuiBreaker.request(request) do
            {:ok, response} -> send_resp(conn, response.status_code, response.body)
            {:error, _reason} -> send_resp(conn, 503, "Service error!")
        end
    end

    post "/register" do
        address = conn.body_params["address"]
        service = conn.body_params["service"]
        ECache.command("LPUSH #{service} #{address}")
        send_resp(conn, 200, service <> " " <> address <> " registed")
    end

    match "/menus/*_rest", do: handle_requests(conn, "menus")
    match "/reports/*_rest", do: handle_requests(conn, "reports")
    match "/orders/*_rest", do: handle_requests(conn, "orders")
    
    match _, do: send_resp(conn, 404, "404. not found!")
    defp handle_errors(conn, err), do: send_resp(conn, 500, err.reason.message)
end
