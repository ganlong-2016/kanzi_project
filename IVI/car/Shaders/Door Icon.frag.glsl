precision highp float;

uniform sampler2D Texture;
uniform float BlendIntensity;

varying vec2 vTexCoord;

void main()
{
    vec4 color = texture2D(Texture, vTexCoord);
    vec2 center = vec2(0.5,0.5);
    float edge = 1.0;
    if(distance(vec2(vTexCoord.x,vTexCoord.y),center)>edge)discard;
    else
    gl_FragColor.rgb = color.rgb * BlendIntensity*0.6;
}
