precision highp float;

// Kanzi默认提供的属性
attribute vec3 kzPosition;
attribute vec2 kzTextureCoordinate0;

// Kanzi默认提供的矩阵
uniform highp mat4 kzProjectionCameraWorldMatrix;
uniform highp mat4 kzWorldMatrix; // 世界变换矩阵

// 自定义参数
uniform float u_BaseSize;         // 基础大小（世界空间单位）
uniform vec2 TextureOffset;
uniform vec2 TextureTiling;

// 相机参数（可通过Kanzi传递或自动计算）
uniform mediump vec3 kzCameraPosition; // 相机世界坐标
uniform float u_ReferenceDistance; // 参考距离（通常设为1.0）

varying vec2 vTexCoord;

void main()
{
    // 1. 计算世界空间位置
    vec4 worldPos = kzWorldMatrix * vec4(kzPosition, 1.0);
    
    // 2. 计算到相机的真实距离（考虑不同控件位置）
    float distance = length(worldPos.xyz - kzCameraPosition);
    
    // 3. 计算动态缩放因子（核心改进）
    float scale = (u_BaseSize * u_ReferenceDistance) / max(distance, 0.001);
    
    // 4. 应用变换（保持各控件比例一致）
    vec4 clipPos = kzProjectionCameraWorldMatrix * vec4(kzPosition / scale*0.055, 1.0);
    
    // 5. 输出最终位置
    gl_Position = clipPos;
    
    // 传递纹理坐标
    vTexCoord = kzTextureCoordinate0 * TextureTiling + TextureOffset;
}