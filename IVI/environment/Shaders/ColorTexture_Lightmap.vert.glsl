attribute vec3 kzPosition;
attribute vec2 kzTextureCoordinate0;
attribute vec2 kzTextureCoordinate1;
uniform highp mat4 kzProjectionCameraWorldMatrix;
uniform mediump vec2 TextureOffset;
uniform mediump vec2 TextureTiling;

varying mediump vec2 vTexCoord;
varying mediump vec2 vTexCoord1;

void main()
{
    precision mediump float;
    
    vTexCoord = kzTextureCoordinate0*TextureTiling + TextureOffset;
    vTexCoord1 = kzTextureCoordinate1;
    gl_Position = kzProjectionCameraWorldMatrix * vec4(kzPosition.xyz, 1.0);
}