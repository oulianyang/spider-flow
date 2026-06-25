package org.spiderflow.websocket;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.spiderflow.core.Spider;
import org.spiderflow.core.utils.SpiderFlowUtils;
import org.spiderflow.model.SpiderWebSocketContext;
import org.spiderflow.model.WebSocketEvent;
import org.springframework.stereotype.Component;

import javax.websocket.OnClose;
import javax.websocket.OnMessage;
import javax.websocket.Session;
import javax.websocket.server.ServerEndpoint;
import java.util.HashMap;
import java.util.Map;

/**
 * WebSocket通讯编辑服务
 *
 * @author Administrator
 */
@ServerEndpoint("/ws")
@Component
public class WebSocketEditorServer {

    public static Spider spider;

    private SpiderWebSocketContext context;

    @OnMessage
    public void onMessage(String message, Session session) {
        JSONObject event = JSON.parseObject(message);
        String eventType = event.getString("eventType");
        boolean isDebug = "debug".equalsIgnoreCase(eventType);
        if ("test".equalsIgnoreCase(eventType) || isDebug) {
            context = new SpiderWebSocketContext(session);
            context.setDebug(isDebug);
            context.setRunning(true);
            // 读取外部项目通过 URL 传入的参数，作为爬虫流程的初始变量
            Map<String, Object> variables = new HashMap<>();
            JSONObject parameters = event.getJSONObject("parameters");
            if (parameters != null) {
                variables.putAll(parameters);
            }
            final Map<String, Object> initVariables = variables;
            new Thread(() -> {
                String xml = event.getString("message");
                if (xml != null) {
                    spider.runWithTest(SpiderFlowUtils.loadXMLFromString(xml), context, initVariables);
                    context.write(new WebSocketEvent<>("finish", null));
                } else {
                    context.write(new WebSocketEvent<>("error", "xml不正确！"));
                }
                context.setRunning(false);
            }).start();
        } else if ("stop".equals(eventType) && context != null) {
            context.setRunning(false);
            context.stop();
        } else if("resume".equalsIgnoreCase(eventType) && context != null){
            context.resume();
        }
    }

    @OnClose
    public void onClose(Session session) {
        context.setRunning(false);
        context.stop();
    }
}
