package org.spiderflow.core.executor.shape;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spiderflow.context.SpiderContext;
import org.spiderflow.model.SpiderNode;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

/**
 * 回调请求执行器
 * <p>
 * 功能与 {@link RequestExecutor} 相同，但 URL 默认值为 {@code ${callback}}，
 * 即从 REST API 参数或 iframe URL 参数中获取回调地址。
 * <p>
 * 典型场景：中台系统通过 iframe 嵌入 spider-flow 编辑器，URL 携带 callback 参数，
 * 爬虫执行完毕后通过该节点回调中台接口存储数据。
 * <p>
 * 使用示例：
 * <ul>
 *   <li>iframe URL: {@code editor.html?id=xxx&callback=http://middle-platform/api/save}</li>
 *   <li>REST API: {@code POST /rest/run/flow123} body: {@code {"callback":"http://middle-platform/api/save"}}</li>
 *   <li>节点 URL 可自定义，不填则默认使用 ${callback}</li>
 * </ul>
 *
 * @author spider-flow
 * @see RequestExecutor
 */
@Component
public class CallbackRequestExecutor extends RequestExecutor {

	private static final Logger logger = LoggerFactory.getLogger(CallbackRequestExecutor.class);

	@Override
	public String supportShape() {
		return "callbackRequest";
	}

	@Override
	public void execute(SpiderNode node, SpiderContext context, Map<String, Object> variables) {
		String url = node.getStringJsonValue(URL);
		// 检测 URL 是否为未经模板引擎求值的原始 JS 表达式（浏览器缓存脏数据问题）
		// 典型特征：以 "d.data.object" 开头，或以 "||" 运算符拼接的表达式
		if (StringUtils.isNotBlank(url) && (url.startsWith("d.data.object") || url.trim().startsWith("d.") || url.contains(" || "))) {
			logger.warn("回调请求节点URL包含未求值的模板表达式，已自动回退至默认值 ${{callback}}，原始值: {}", url);
			url = null;
		}
		// 回调节点需要修改节点属性时，创建副本避免污染原始节点数据（线程安全）
		Map<String, Object> nodeProps = null;
		if (StringUtils.isBlank(url)) {
			nodeProps = new HashMap<>(node.getJsonProperty());
			nodeProps.put(URL, "${callback}");
			logger.debug("回调请求节点未配置URL，使用默认回调地址: ${{callback}}");
		}
		// 回调场景通常向回调地址提交数据，当配置了 Body 但请求方法仍为 GET 时，自动升级为 POST
		String method = node.getStringJsonValue(REQUEST_METHOD);
		String bodyType = node.getStringJsonValue(BODY_TYPE);
		if (("GET".equalsIgnoreCase(method) || method == null) &&
				("raw".equals(bodyType) || "form-data".equals(bodyType))) {
			if (nodeProps == null) {
				nodeProps = new HashMap<>(node.getJsonProperty());
			}
			nodeProps.put(REQUEST_METHOD, "POST");
			logger.info("回调请求节点已自动将请求方法从 GET 升级为 POST（检测到 Body 类型为 {}）", bodyType);
		}
		if (nodeProps != null) {
			node.setJsonProperty(nodeProps);
		}
		// 验证 callback 变量是否存在
		Object callbackUrl = variables.get("callback");
		if (callbackUrl == null || StringUtils.isBlank(callbackUrl.toString())) {
			logger.warn("回调请求节点：变量中未找到 callback 参数，请确保通过 REST API 或 iframe URL 传入 callback 地址");
		}
		super.execute(node, context, variables);
	}
}
