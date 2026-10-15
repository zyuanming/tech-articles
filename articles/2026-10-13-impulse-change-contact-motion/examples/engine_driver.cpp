// Original MIT-licensed article driver. Uses unmodified Box2D-Lite core.
#include "box2d-lite/World.h"
#include "box2d-lite/Body.h"
#include <cstdio>
#include <cstdlib>
#include <array>
#include <string>
int main(int argc,char**argv){
  std::string scene=argc>1?argv[1]:"offset";
  int iterations=argc>2?std::atoi(argv[2]):10;
  bool warm=argc>3?std::atoi(argv[3])!=0:true;
  float friction=argc>4?std::atof(argv[4]):0.3f;
  float dt=scene=="offset"||scene=="center"?1.f/240.f:1.f/60.f;
  int count=scene=="stack"?9:scene=="slide"?2:2;
  int frames=scene=="stack"?600:scene=="slide"?240:360;
  std::array<Body,12> bodies;
  World world(Vec2(0,scene=="stack"||scene=="slide"?-10.f:0),iterations);
  World::warmStarting=warm;World::accumulateImpulses=true;
  World::positionCorrection=scene=="stack"||scene=="slide";
  if(scene=="stack"||scene=="slide"){
    bodies[0].Set(Vec2(50,1),FLT_MAX);bodies[0].position.Set(0,-.5f);bodies[0].friction=friction;
    for(int i=1;i<count;i++){bodies[i].Set(Vec2(1,1),1);bodies[i].position.Set(scene=="slide"?-4:0,.51f+(i-1)*1.01f);bodies[i].friction=friction;}
    if(scene=="slide")bodies[1].velocity.Set(5,0);
  }else{
    for(int i=0;i<count;i++){bodies[i].Set(Vec2(1,1),1);bodies[i].friction=0;}
    bodies[0].position.Set(-2,scene=="offset"?.65f:0);bodies[0].velocity.Set(4,0);bodies[1].position.Set(0,0);
  }
  for(int i=0;i<count;i++)world.Add(&bodies[i]);
  std::puts("frame,time,body,x,y,angle,vx,vy,omega,width,height,mass,contacts,max_penetration");
  for(int frame=0;frame<=frames;frame++){
    int contacts=0;float pen=0;
    for(auto&kv:world.arbiters){contacts+=kv.second.numContacts;for(int j=0;j<kv.second.numContacts;j++)pen=Max(pen,-kv.second.contacts[j].separation);}
    for(int i=0;i<count;i++){auto&b=bodies[i];std::printf("%d,%.9g,%d,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%.9g,%d,%.9g\n",frame,frame*dt,i,b.position.x,b.position.y,b.rotation,b.velocity.x,b.velocity.y,b.angularVelocity,b.width.x,b.width.y,b.mass,contacts,pen);}
    if(frame<frames)world.Step(dt);
  }
}
