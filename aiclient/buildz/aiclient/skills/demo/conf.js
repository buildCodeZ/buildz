//测试用，没实际作用
{
  @fc=skills.demo.test.hashval
  @folder="../.."
  name=calhash
  description: "计算字符串的hash值",
  parameters: {
    type: object
    "properties": {
      "text": {
        type: "string",
        description: "要生成hash值的字符串"
      },
      "alg":{
        type: "string",
        "enum": ["md5", "sha256"],
        description: "hash算法，默认md5"
      }
      "coding": {
        type: "string",
        "enum": ["utf-8", "gbk", "ascii"],
        description: "字符串编码格式，默认utf-8"
      }
    },
    required: ["text"]
  }
}
{
  @fc=skills.demo.test.base64_encode
  name: "base64_encode",
  description: "计算字符串的base64编码值",
  "parameters": {
    type: "object",
    "properties": {
      "text": {
        type: "string",
        description: "要生成base64编码的字符串"
      },
      "coding": {
        type: "string",
        "enum": ["utf-8", "gbk", "ascii"],
        description: "字符串编码格式，默认utf-8"
      }
    },
    required: ["text"]
  }
}

{
  @fc=skills.demo.test.base64_decode
  name: "base64_decode",
  description: "计算base64编码字符串的解码结果",
  "parameters": {
    type: "object",
    "properties": {
      "text": {
        type: "string",
        description: "base64编码字符串"
      },
      "coding": {
        type: "string",
        "enum": ["utf-8", "gbk", "ascii"],
        description: "解码后字符串编码格式，默认utf-8"
      }
    },
    required: ["text"]
  }
}
