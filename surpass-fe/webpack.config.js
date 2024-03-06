
const path = require('path');

module.exports = {
  // 入口文件配置
//   entry: './src/index.js',

  // 输出文件配置
//   output: {
//     path: path.resolve(__dirname, 'dist'),
//     filename: 'bundle.js',
//   },

  // 开发服务器配置
  devServer: {
    // 代理配置
    proxy: {
      // 当你请求 "/api" 路径时，代理会将请求转发到 "http://example.com" 上
      '/api': {
        target: 'https://surpass-be-sxjkzgaaeq-uw.a.run.app/api',
        changeOrigin: true, // 为了虚拟托管站点，需要更改origin
        pathRewrite: { '^/api': '' }, // 重写路径，去掉路径中的"/api"
      },
    },
  },
};
